from django import template
from django.utils.html import escape, format_html, linebreaks
from django.utils.safestring import mark_safe


register = template.Library()


@register.filter
def post_content(post):
    content = escape(post.content)
    for link in post.links.all():
        label = escape(link.label)
        anchor = format_html(
            '<a href="{}" target="_blank" rel="noopener noreferrer">{}</a>',
            link.url,
            link.label,
        )
        content = content.replace(label, str(anchor))
    return mark_safe(linebreaks(content))
