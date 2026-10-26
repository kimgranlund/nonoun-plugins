// Scheme qualification precedes task assertions, including the effective preview document.
export async function qualifyScheme(page,scope,requested,settle){
 const control=page.locator('#color-scheme');
 for(let i=0;i<3&&await control.getAttribute('data-scheme')!==requested;i++){await control.click();await settle();}
 const actual=await control.getAttribute('data-scheme');
 const effective=await scope.locator('html').evaluate(e=>({scheme:getComputedStyle(e).colorScheme,os:matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light'}));
 if(actual!==requested||effective.scheme!==requested)throw Error(`Scheme mismatch: requested ${requested}; control ${actual}; preview ${effective.scheme}; OS ${effective.os}`);
 return {requested,control:actual,effective:effective.scheme,emulatedOS:effective.os};
}
