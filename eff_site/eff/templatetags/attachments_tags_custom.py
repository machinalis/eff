from attachments.forms import AttachmentForm
from attachments.views import add_url_for_obj
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.db.models import get_model
from django import template
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import smart_unicode

register = template.Library()


@register.inclusion_tag('attachments/delete_link.html', takes_context=True)
def attachment_delete_link(context, attachment):
    """
Renders a html link to the delete view of the given attachment. Returns
no content if the request-user has no permission to delete attachments.
The user must own either the ``attachments.delete_attachment`` permission
and is the creator of the attachment, that he can delete it or he has
``attachments.delete_foreign_attachments`` which allows him to delete all
attachments.
"""
    if context['user'].has_perm('delete_foreign_attachments') \
       or (context['user'] == attachment.creator and \
           context['user'].has_perm('attachments.delete_attachment')):
        return {
            'next': context['request'].build_absolute_uri(),
            'delete_url': reverse('delete_attachment',
                                  kwargs={'attachment_pk': attachment.pk})
        }
    return {'delete_url': None}


class BaseAttachmentNode(template.Node):
    """
    Base helper class (abstract) for handling the get_attachment_* template
    tags.
    """

    @classmethod
    def handle_token(cls, parser, token):
        """
        Class method to parse get_attachment_list/form and return a Node.
        """
        tokens = token.contents.split()
        if tokens[1] != 'for':
            raise template.TemplateSyntaxError(
                "Second argument in %r tag must be 'for'" % tokens[0])

        # {% get_whatever for obj as varname %}
        if len(tokens) == 5:
            if tokens[3] != 'as':
                raise template.TemplateSyntaxError(
                    "Third argument in %r must be 'as'" % tokens[0])
            return cls(object_expr=parser.compile_filter(tokens[2]),
                       as_varname=tokens[4])

        # {% get_whatever for app.model pk as varname %}
        elif len(tokens) == 6:
            if tokens[4] != 'as':
                raise template.TemplateSyntaxError(
                    "Fourth argument in %r must be 'as'" % tokens[0])
            return cls(
                ctype=BaseAttachmentNode.lookup_content_type(tokens[2],
                                                             tokens[0]),
                object_id_expr=parser.compile_filter(tokens[3]),
                as_varname=tokens[5]
                )

        else:
            raise template.TemplateSyntaxError(
                "%r tag requires 4 or 5 arguments" % tokens[0])

    @staticmethod
    def lookup_content_type(token, tagname):
        try:
            app, model = token.split('.')
            return ContentType.objects.get_by_natural_key(app, model)
        except ValueError:
            _error = "Third argument in %r must be in the format 'app.model'"
            raise template.TemplateSyntaxError(_error % tagname)
        except ContentType.DoesNotExist:
            _error = "%r tag has non-existant content-type: '%s.%s'"
            raise template.TemplateSyntaxError(_error % (tagname, app, model))

    def __init__(self, ctype=None, object_id_expr=None, object_expr=None,
                 as_varname=None, attachment=None):
        if ctype is None and object_expr is None:
            _error = ("Attachment nodes must be given either a literal object"
                      " or a ctype and object pk.")
            raise template.TemplateSyntaxError(_error)
        self.attachment_model = get_model('attachments', 'attachment')
        self.as_varname = as_varname
        self.ctype = ctype
        self.object_id_expr = object_id_expr
        self.object_expr = object_expr
        self.attachment = attachment

    def render(self, context):
        qs = self.get_query_set(context)
        context[self.as_varname] = self.get_context_value_from_queryset(context,
                                                                        qs)
        return ''

    def get_query_set(self, context):
        ctype, object_id = self.get_target_ctype_pk(context)
        if not object_id:
            return self.attachment_model.objects.none()

        qs = self.attachment_model.objects.filter(
            content_type=ctype,
            object_id=smart_unicode(object_id),
            )

        return qs

    def get_target_ctype_pk(self, context):
        if self.object_expr:
            try:
                obj = self.object_expr.resolve(context)
            except template.VariableDoesNotExist:
                return None, None
            return ContentType.objects.get_for_model(obj), obj.pk
        else:
            return self.ctype, self.object_id_expr.resolve(context,
                                                           ignore_failures=True)

    def get_context_value_from_queryset(self, context, qs):
        """Subclasses should override this."""
        raise NotImplementedError


class AttachmentListNode(BaseAttachmentNode):
    """Insert a list of attachments into the context."""
    def get_context_value_from_queryset(self, context, qs):
        return list(qs)


class AttachmentFormNode(BaseAttachmentNode):
    """Insert a form for the attachment model into the context."""

    def get_form(self, context):
        obj = self.get_object(context)
        if obj and context['user'].has_perm('attachments.add_attachment'):
            if 'form' in context:
                return context['form']
            else:
                return AttachmentForm()
        else:
            return None

    def get_object(self, context):
        if self.object_expr:
            try:
                return self.object_expr.resolve(context)
            except template.VariableDoesNotExist:
                return None
        else:
            object_id = self.object_id_expr.resolve(context,
                    ignore_failures=True)
            return self.ctype.get_object_for_this_type(pk=object_id)

    def render(self, context):
        obj = self.get_object(context)
        context[self.as_varname] = self.get_form(context)
        context['form_url'] = add_url_for_obj(obj)
        context['object_id'] = obj.id
        return ''


class RenderAttachmentFormNode(AttachmentFormNode):
    """Render the attachments form directly"""

    @classmethod
    def handle_token(cls, parser, token):
        """Class method to parse render_attachment_form and return a Node."""
        tokens = token.contents.split()
        if tokens[1] != 'for':
            raise template.TemplateSyntaxError(
                "Second argument in %r tag must be 'for'" % tokens[0])

        # {% render_attachment_form for obj %}
        if len(tokens) == 3:
            return cls(object_expr=parser.compile_filter(tokens[2]))

        # {% render_attachment_form for app.models pk %}
        elif len(tokens) == 4:
            return cls(
                ctype=BaseAttachmentNode.lookup_content_type(tokens[2],
                                                               tokens[0]),
                object_id_expr=parser.compile_filter(tokens[3])
                )

    def render(self, context):
        ctype, object_id = self.get_target_ctype_pk(context)
        obj = self.get_object(context)
        if object_id:
            template_search_list = ["attachments/add_form.html"]
            context.push()
            formstr = render_to_string(template_search_list,
                                       {'form': self.get_form(context),
                                        'form_url': add_url_for_obj(obj),
                                        'object_id': obj.id},
                                       context)
            context.pop()
            return formstr
        else:
            return ''


class RenderAttachmentListNode(AttachmentListNode):
    """Render the attachment list directly"""

    @classmethod
    def handle_token(cls, parser, token):
        """Class method to parse render_attachment_list and return a Node."""
        tokens = token.contents.split()
        if tokens[1] != 'for':
            raise template.TemplateSyntaxError(
                "Second argument in %r tag must be 'for'" % tokens[0])

        # {% render_attachment_list for obj %}
        if len(tokens) == 3:
            return cls(object_expr=parser.compile_filter(tokens[2]))

        # {% render_attachment_list for app.models pk %}
        elif len(tokens) == 4:
            return cls(
                ctype=BaseAttachmentNode.lookup_content_type(tokens[2],
                                                             tokens[0]),
                object_id_expr=parser.compile_filter(tokens[3])
                )

    def render(self, context):
        ctype, object_id = self.get_target_ctype_pk(context)
        if object_id:
            template_search_list = ["attachments/list.html"]
            qs = self.get_query_set(context)
            context.push()
            liststr = render_to_string(template_search_list,
            {"attachment_list": self.get_context_value_from_queryset(context,
                                                                     qs)},
                                       context)
            context.pop()
            return liststr
        else:
            return ''


# Each node gets a cute wrapper function that just exists to hold the docstring.

@register.tag
def get_attachment_list(parser, token):
    """
Gets the list of attachments for the given params and populates the template
context with a variable containing that value, whose name is defined by the
'as' clause.

Syntax::

{% get_attachment_list for [object] as [varname] %}
{% get_attachment_list for [app].[model] [object_id] as [varname] %}

Example usage::

{% get_attachment_list for event as attachment_list %}
{% for attachment in attachment_list %}
...
{% endfor %}

"""
    return AttachmentListNode.handle_token(parser, token)


@register.tag
def render_attachment_list(parser, token):
    """
Render the attachment list (as returned by ``{% get_attachment_list %}``)
through the ``attachments/list.html`` template

Syntax::

{% render_attachment_list for [object] %}
{% render_attachment_list for [app].[model] [object_id] %}

Example usage::

{% render_attachment_list for event %}

"""
    return RenderAttachmentListNode.handle_token(parser, token)


@register.tag
def get_attachment_form(parser, token):
    """
Get a (new) form object to post a new attachment.

Syntax::

{% get_attachment_form for [object] as [varname] %}
{% get_attachment_form for [app].[model] [object_id] as [varname] %}
"""
    return AttachmentFormNode.handle_token(parser, token)


@register.tag
def render_attachment_form(parser, token):
    """
Render the attachment form (as returned by ``{% render_attachment_form %}``)
through the ``attachments/add_form.html`` template.

Syntax::

{% render_attachment_form for [object] %}
{% render_attachment_form for [app].[model] [object_id] %}
"""
    return RenderAttachmentFormNode.handle_token(parser, token)
