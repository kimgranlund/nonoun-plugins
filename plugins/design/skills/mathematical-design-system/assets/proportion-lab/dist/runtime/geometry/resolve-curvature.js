                                            
/** Nominal radius; CSS additionally fits to actual box width. */
export function resolveCurvature(curvature           , unit        , height        , family                       ='control', width=Infinity) {
 const coefficients={sharpest:0,sharp:1,default:2,soft:3,softest:4};
 const requested=curvature==='softest' && family==='control' ? height/2 : coefficients[curvature]*unit;
 return Math.max(0,Math.min(requested,height/2,width/2));
}
export function resolveNestedRadius(parentRadius       ,edgeDistance       ,childHeight       ,requestedInset       ) {
 return requestedInset===0 ? 0 : Math.min(childHeight/2,Math.max(0,parentRadius-edgeDistance));
}
