// Canonical select anatomy shared by generation and explicit dynamic construction.
export const SELECT_INDICATOR = "<span data-slot=\"indicator\" aria-hidden=\"true\"><svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 256 256\" fill=\"currentColor\" aria-hidden=\"true\" focusable=\"false\"><path fill=\"currentColor\" stroke=\"none\" d=\"M213.66,101.66l-80,80a8,8,0,0,1-11.32,0l-80-80A8,8,0,0,1,53.66,90.34L128,164.69l74.34-74.35a8,8,0,0,1,11.32,11.32Z\"/></svg></span>";
export function createSelectControl(doc=document) {
  const root=doc.createElement('span');root.className='select__root';
  const select=doc.createElement('select');root.append(select);
  const template=doc.createElement('template');template.innerHTML=SELECT_INDICATOR;
  root.append(template.content.cloneNode(true));
  return {root,select};
}
