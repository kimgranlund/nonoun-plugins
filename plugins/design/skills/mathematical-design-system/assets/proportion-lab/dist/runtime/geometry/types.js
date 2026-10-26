                                                      
                                                                              
                                                                                                                                  
export function inputs(input                = {}) {
 const {unit=4,border=0,density='default',curvature='soft',labelEdgeUnits=1.5}=input;
 if (!Number.isFinite(unit)||unit<3||unit>6) throw new RangeError('unit must be 3..6 CSS px');
 if (!Number.isFinite(border)||border<0||border>unit/2) throw new RangeError('border must be 0..u/2');
 if (!Number.isFinite(labelEdgeUnits)||labelEdgeUnits<0||labelEdgeUnits>3) throw new RangeError('label edge must be 0..3u');
 const index=['compact','default','loose'].indexOf(density);
 if(index<0) throw new RangeError('unknown density');
 if(!['sharpest','sharp','default','soft','softest'].includes(curvature)) throw new RangeError('unknown curvature');
 return {unit,border,density,curvature,labelEdgeUnits,index};
}
