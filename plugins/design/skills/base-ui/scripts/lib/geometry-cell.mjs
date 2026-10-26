// Shared kit projection of one resolved mathematical geometry value.
export function geometryCell(v){return {
      height:v.surface.height, margin:v.n, text:v.type.control, icon:v.surface.icon,
      'caption-text':v.type.fieldLabel, 'small-control-text':v.type.smallControl, 'chip-height':3*v.n, 'compact-height':3*v.n, 'chip-margin':2*v.c,
      'chip-text':v.type.fieldLabel, 'icon-height-ratio':.5, 'listbox-margin':v.c, 'listbox-gutter':v.c,
      'field-gutter':v.n/2, glyph:v.surface.glyph, 'radio-dot':2*v.n-4*v.c,
      'body-text':v.type.body, 'title-text':v.type.title,
      'heading-text':v.type.heading, 'display-text':v.type.display,
      'subhead-text':v.type.subhead, 'section-kicker-text':v.type.sectionKicker,
      'group-kicker-text':v.type.groupKicker,
    };}
