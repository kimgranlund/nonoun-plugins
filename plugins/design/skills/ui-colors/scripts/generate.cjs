/*!
colorjs-LICENSE
MIT License

Copyright (c) 2021 Lea Verou, Chris Lilley

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


ultimate-tokens-LICENSE
MIT License

Copyright (c) 2026 Kim Granlund

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

*/
"use strict";var Bs=Object.create;var Yr=Object.defineProperty;var $s=Object.getOwnPropertyDescriptor;var zs=Object.getOwnPropertyNames;var Gs=Object.getPrototypeOf,Ws=Object.prototype.hasOwnProperty;var Ut=(r,e)=>{for(var t in e)Yr(r,t,{get:e[t],enumerable:!0})},Us=(r,e,t,n)=>{if(e&&typeof e=="object"||typeof e=="function")for(let o of zs(e))!Ws.call(r,o)&&o!==t&&Yr(r,o,{get:()=>e[o],enumerable:!(n=$s(e,o))||n.enumerable});return r};var Xt=(r,e,t)=>(t=r!=null?Bs(Gs(r)):{},Us(e||!r||!r.__esModule?Yr(t,"default",{value:r,enumerable:!0}):t,r));var Ur=Xt(require("node:fs/promises"),1),Gt=Xt(require("node:path"),1);var Vr="source-policies@1",Vt=r=>r!==null&&typeof r=="object"&&!Array.isArray(r)&&[Object.prototype,null].includes(Object.getPrototypeOf(r)),Yt=(r,e)=>Vt(r)&&Object.keys(r).every(t=>e.includes(t));function Zt(r,e){if(!Yt(r,["version","rules"])||r.version!==Vr||!Vt(r.rules))throw new TypeError("Invalid or unsupported source policy version");for(let[a,i]of Object.entries(r.rules))if(!Object.hasOwn(e,a)||!Yt(i,["kind","family","achromatic"])||i.kind!=="hue-from"||i.achromatic!=="authored-hue"||typeof i.family!="string"||!Object.hasOwn(e,i.family)||i.family===a)throw new TypeError(`Invalid hue source policy: ${a}`);let t=r,n=new Set,o=new Set,s=a=>{if(n.has(a))throw new TypeError("Source policy dependency cycle");if(o.has(a))return;n.add(a);let i=Object.hasOwn(t.rules,a)?t.rules[a]:null;i&&s(i.family),n.delete(a),o.add(a)};return Object.keys(e).forEach(s),t}var ur=Object.freeze(["srgb","display-p3","xyz-d65","xyz-d50","oklab","oklch"]),Pe=class extends TypeError{path;constructor(e,t){super(`${e}: ${t}`),this.name="ColorValidationError",this.path=e}},K=(r,e)=>{throw new Pe(r,e)};function Zr(r,e,t){(!r||typeof r!="object"||Array.isArray(r)||![Object.prototype,null].includes(Object.getPrototypeOf(r)))&&K(e,"expected a plain object");for(let n of Object.keys(r))t.includes(n)||K(`${e}.${n}`,"unknown field")}var Jr=(r,e)=>Object.hasOwn(r,e);function Kr(r,e,t){for(let n of e)Jr(r,n)||K(`${t}.${n}`,"required field")}function Kt(r,e){(typeof r!="number"||!Number.isFinite(r))&&K(e,"expected a finite number")}function he(r,e="color"){Zr(r,e,["colorSpace","components","alpha","provenance"]),Kr(r,["colorSpace","components","alpha"],e),ur.includes(r.colorSpace)||K(`${e}.colorSpace`,"unsupported color space"),(!Array.isArray(r.components)||r.components.length!==3)&&K(`${e}.components`,"expected three coordinates");for(let t=0;t<3;t++)Kt(r.components[t],`${e}.components[${t}]`);if(r.colorSpace==="oklch"&&r.components[1]<0&&K(`${e}.components[1]`,"chroma must be nonnegative"),Kt(r.alpha,`${e}.alpha`),(r.alpha<0||r.alpha>1)&&K(`${e}.alpha`,"expected alpha in [0,1]"),Jr(r,"provenance")){Zr(r.provenance,`${e}.provenance`,["description","originalInput"]);let t=r.provenance;for(let n of Object.keys(t))typeof t[n]!="string"&&K(`${e}.provenance.${n}`,"expected a string")}return r}function Qr(r){Zr(r,"document",["$schema","schemaVersion","colors",...r?.schemaVersion===2?["sourcePolicies"]:[]]),Kr(r,["schemaVersion","colors"],"document"),[1,2].includes(r.schemaVersion)||K("document.schemaVersion","unsupported schema version"),Jr(r,"$schema")&&typeof r.$schema!="string"&&K("document.$schema","expected a string");let e=r.colors;(!e||typeof e!="object"||Array.isArray(e)||![Object.prototype,null].includes(Object.getPrototypeOf(e)))&&K("document.colors","expected a plain object"),Object.keys(e).length||K("document.colors","at least one color is required");for(let[t,n]of Object.entries(e))/^[a-z][a-z0-9-]*$/.test(t)||K(`document.colors.${t}`,"invalid color identifier"),he(n,`document.colors.${t}`);return r.schemaVersion===2&&(Kr(r,["sourcePolicies"],"document"),Zt(r.sourcePolicies,e)),r}var Ue={};Ut(Ue,{atan2:()=>de,cbrt:()=>ae,cos:()=>$,sin:()=>U});var Xs=Object.create,Jt=Object.defineProperty,Ys=Object.getOwnPropertyDescriptor,Qt=Object.getOwnPropertyNames,Vs=Object.getPrototypeOf,Zs=Object.prototype.hasOwnProperty,b=(r,e)=>function(){return e||(0,r[Qt(r)[0]])((e={exports:{}}).exports,e),e.exports},Ks=(r,e,t,n)=>{if(e&&typeof e=="object"||typeof e=="function")for(let o of Qt(e))!Zs.call(r,o)&&o!==t&&Jt(r,o,{get:()=>e[o],enumerable:!(n=Ys(e,o))||n.enumerable});return r},mr=(r,e,t)=>(t=r!=null?Xs(Vs(r)):{},Ks(e||!r||!r.__esModule?Jt(t,"default",{value:r,enumerable:!0}):t,r)),Be=b({"node_modules/@stdlib/constants-float64-high-word-abs-mask/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2022 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=2147483647;e.exports=t}}),pr=b({"node_modules/@stdlib/constants-float64-high-word-exponent-mask/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=2146435072;e.exports=t}}),Js=b({"node_modules/@stdlib/assert-has-symbol-support/lib/main.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/function t(){return typeof Symbol=="function"&&typeof Symbol("foo")=="symbol"}e.exports=t}}),Qs=b({"node_modules/@stdlib/assert-has-symbol-support/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=Js();e.exports=t}}),ea=b({"node_modules/@stdlib/assert-has-tostringtag-support/lib/main.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=Qs(),n=t();function o(){return n&&typeof Symbol.toStringTag=="symbol"}e.exports=o}}),ra=b({"node_modules/@stdlib/assert-has-tostringtag-support/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=ea();e.exports=t}}),en=b({"node_modules/@stdlib/utils-native-class/lib/tostring.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=Object.prototype.toString;e.exports=t}}),ta=b({"node_modules/@stdlib/utils-native-class/lib/main.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=en();function n(o){return t.call(o)}e.exports=n}}),na=b({"node_modules/@stdlib/assert-has-own-property/lib/main.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=Object.prototype.hasOwnProperty;function n(o,s){return o==null?!1:t.call(o,s)}e.exports=n}}),oa=b({"node_modules/@stdlib/assert-has-own-property/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=na();e.exports=t}}),sa=b({"node_modules/@stdlib/symbol-ctor/lib/main.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=typeof Symbol=="function"?Symbol:void 0;e.exports=t}}),aa=b({"node_modules/@stdlib/symbol-ctor/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=sa();e.exports=t}}),ia=b({"node_modules/@stdlib/utils-native-class/lib/tostringtag.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=aa(),n=typeof t=="function"?t.toStringTag:"";e.exports=n}}),la=b({"node_modules/@stdlib/utils-native-class/lib/polyfill.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=oa(),n=ia(),o=en();function s(a){var i,l,u;if(a==null)return o.call(a);l=a[n],i=t(a,n);try{a[n]=void 0}catch{return o.call(a)}return u=o.call(a),i?a[n]=l:delete a[n],u}e.exports=s}}),dr=b({"node_modules/@stdlib/utils-native-class/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=ra(),n=ta(),o=la(),s;t()?s=o:s=n,e.exports=s}}),ca=b({"node_modules/@stdlib/assert-is-uint32array/lib/main.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=dr(),n=typeof Uint32Array=="function";function o(s){return n&&s instanceof Uint32Array||t(s)==="[object Uint32Array]"}e.exports=o}}),ua=b({"node_modules/@stdlib/assert-is-uint32array/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=ca();e.exports=t}}),ma=b({"node_modules/@stdlib/constants-uint32-max/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=4294967295;e.exports=t}}),pa=b({"node_modules/@stdlib/assert-has-uint32array-support/lib/uint32array.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=typeof Uint32Array=="function"?Uint32Array:null;e.exports=t}}),da=b({"node_modules/@stdlib/assert-has-uint32array-support/lib/main.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=ua(),n=ma(),o=pa();function s(){var a,i;if(typeof o!="function")return!1;try{i=[1,3.14,-3.14,n+1,n+2],i=new o(i),a=t(i)&&i[0]===1&&i[1]===3&&i[2]===n-2&&i[3]===0&&i[4]===1}catch{a=!1}return a}e.exports=s}}),fa=b({"node_modules/@stdlib/assert-has-uint32array-support/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=da();e.exports=t}}),ha=b({"node_modules/@stdlib/array-uint32/lib/main.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=typeof Uint32Array=="function"?Uint32Array:void 0;e.exports=t}}),ba=b({"node_modules/@stdlib/array-uint32/lib/polyfill.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/function t(){throw new Error("not implemented")}e.exports=t}}),$e=b({"node_modules/@stdlib/array-uint32/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=fa(),n=ha(),o=ba(),s;t()?s=n:s=o,e.exports=s}}),ga=b({"node_modules/@stdlib/assert-is-float64array/lib/main.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=dr(),n=typeof Float64Array=="function";function o(s){return n&&s instanceof Float64Array||t(s)==="[object Float64Array]"}e.exports=o}}),va=b({"node_modules/@stdlib/assert-is-float64array/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=ga();e.exports=t}}),ya=b({"node_modules/@stdlib/assert-has-float64array-support/lib/float64array.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=typeof Float64Array=="function"?Float64Array:null;e.exports=t}}),_a=b({"node_modules/@stdlib/assert-has-float64array-support/lib/main.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=va(),n=ya();function o(){var s,a;if(typeof n!="function")return!1;try{a=new n([1,3.14,-3.14,NaN]),s=t(a)&&a[0]===1&&a[1]===3.14&&a[2]===-3.14&&a[3]!==a[3]}catch{s=!1}return s}e.exports=o}}),xa=b({"node_modules/@stdlib/assert-has-float64array-support/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=_a();e.exports=t}}),Sa=b({"node_modules/@stdlib/array-float64/lib/main.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=typeof Float64Array=="function"?Float64Array:void 0;e.exports=t}}),wa=b({"node_modules/@stdlib/array-float64/lib/polyfill.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/function t(){throw new Error("not implemented")}e.exports=t}}),ze=b({"node_modules/@stdlib/array-float64/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=xa(),n=Sa(),o=wa(),s;t()?s=n:s=o,e.exports=s}}),Ma=b({"node_modules/@stdlib/assert-is-uint8array/lib/main.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=dr(),n=typeof Uint8Array=="function";function o(s){return n&&s instanceof Uint8Array||t(s)==="[object Uint8Array]"}e.exports=o}}),Ca=b({"node_modules/@stdlib/assert-is-uint8array/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=Ma();e.exports=t}}),Oa=b({"node_modules/@stdlib/constants-uint8-max/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=255;e.exports=t}}),Ra=b({"node_modules/@stdlib/assert-has-uint8array-support/lib/uint8array.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=typeof Uint8Array=="function"?Uint8Array:null;e.exports=t}}),Ta=b({"node_modules/@stdlib/assert-has-uint8array-support/lib/main.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=Ca(),n=Oa(),o=Ra();function s(){var a,i;if(typeof o!="function")return!1;try{i=[1,3.14,-3.14,n+1,n+2],i=new o(i),a=t(i)&&i[0]===1&&i[1]===3&&i[2]===n-2&&i[3]===0&&i[4]===1}catch{a=!1}return a}e.exports=s}}),Pa=b({"node_modules/@stdlib/assert-has-uint8array-support/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=Ta();e.exports=t}}),Ea=b({"node_modules/@stdlib/array-uint8/lib/main.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=typeof Uint8Array=="function"?Uint8Array:void 0;e.exports=t}}),ka=b({"node_modules/@stdlib/array-uint8/lib/polyfill.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/function t(){throw new Error("not implemented")}e.exports=t}}),ja=b({"node_modules/@stdlib/array-uint8/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=Pa(),n=Ea(),o=ka(),s;t()?s=n:s=o,e.exports=s}}),Aa=b({"node_modules/@stdlib/assert-is-uint16array/lib/main.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=dr(),n=typeof Uint16Array=="function";function o(s){return n&&s instanceof Uint16Array||t(s)==="[object Uint16Array]"}e.exports=o}}),Ia=b({"node_modules/@stdlib/assert-is-uint16array/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=Aa();e.exports=t}}),Na=b({"node_modules/@stdlib/constants-uint16-max/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=65535;e.exports=t}}),La=b({"node_modules/@stdlib/assert-has-uint16array-support/lib/uint16array.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=typeof Uint16Array=="function"?Uint16Array:null;e.exports=t}}),qa=b({"node_modules/@stdlib/assert-has-uint16array-support/lib/main.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=Ia(),n=Na(),o=La();function s(){var a,i;if(typeof o!="function")return!1;try{i=[1,3.14,-3.14,n+1,n+2],i=new o(i),a=t(i)&&i[0]===1&&i[1]===3&&i[2]===n-2&&i[3]===0&&i[4]===1}catch{a=!1}return a}e.exports=s}}),Ha=b({"node_modules/@stdlib/assert-has-uint16array-support/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=qa();e.exports=t}}),Fa=b({"node_modules/@stdlib/array-uint16/lib/main.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=typeof Uint16Array=="function"?Uint16Array:void 0;e.exports=t}}),Da=b({"node_modules/@stdlib/array-uint16/lib/polyfill.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/function t(){throw new Error("not implemented")}e.exports=t}}),Ba=b({"node_modules/@stdlib/array-uint16/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=Ha(),n=Fa(),o=Da(),s;t()?s=n:s=o,e.exports=s}}),$a=b({"node_modules/@stdlib/assert-is-little-endian/lib/ctors.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=ja(),n=Ba(),o={uint16:n,uint8:t};e.exports=o}}),za=b({"node_modules/@stdlib/assert-is-little-endian/lib/main.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=$a(),n;function o(){var s,a;return s=new t.uint16(1),s[0]=4660,a=new t.uint8(s.buffer),a[0]===52}n=o(),e.exports=n}}),Ge=b({"node_modules/@stdlib/assert-is-little-endian/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=za();e.exports=t}}),Ga=b({"node_modules/@stdlib/number-float64-base-get-high-word/lib/high.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=Ge(),n;t===!0?n=1:n=0,e.exports=n}}),Wa=b({"node_modules/@stdlib/number-float64-base-get-high-word/lib/main.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=$e(),n=ze(),o=Ga(),s=new n(1),a=new t(s.buffer);function i(l){return s[0]=l,a[o]}e.exports=i}}),be=b({"node_modules/@stdlib/number-float64-base-get-high-word/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=Wa();e.exports=t}}),Ua=b({"node_modules/@stdlib/math-base-special-kernel-cos/lib/polyval_c13.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2022 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/function t(n){return n===0?.0416666666666666:.0416666666666666+n*(-.001388888888887411+n*2480158728947673e-20)}e.exports=t}}),Xa=b({"node_modules/@stdlib/math-base-special-kernel-cos/lib/polyval_c46.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2022 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/function t(n){return n===0?-27557314351390663e-23:-27557314351390663e-23+n*(2087572321298175e-24+n*-11359647557788195e-27)}e.exports=t}}),Ya=b({"node_modules/@stdlib/math-base-special-kernel-cos/lib/main.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*
*
* ## Notice
*
* The following copyright, license, and long comment were part of the original implementation available as part of [FreeBSD]{@link https://svnweb.freebsd.org/base/release/12.2.0/lib/msun/src/k_cos.c}. The implementation follows the original, but has been modified for JavaScript.
*
* ```text
* Copyright (C) 1993 by Sun Microsystems, Inc. All rights reserved.
*
* Developed at SunPro, a Sun Microsystems, Inc. business.
* Permission to use, copy, modify, and distribute this
* software is freely granted, provided that this notice
* is preserved.
* ```
*/var t=Ua(),n=Xa();function o(s,a){var i,l,u,c;return c=s*s,u=c*c,l=c*t(c),l+=u*u*n(c),i=.5*c,u=1-i,u+(1-u-i+(c*l-s*a))}e.exports=o}}),rn=b({"node_modules/@stdlib/math-base-special-kernel-cos/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=Ya();e.exports=t}}),Va=b({"node_modules/@stdlib/math-base-special-kernel-sin/lib/main.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*
*
* ## Notice
*
* The following copyright, license, and long comment were part of the original implementation available as part of [FreeBSD]{@link https://svnweb.freebsd.org/base/release/9.3.0/lib/msun/src/k_sin.c}. The implementation follows the original, but has been modified for JavaScript.
*
* ```text
* Copyright (C) 1993 by Sun Microsystems, Inc. All rights reserved.
*
* Developed at SunPro, a Sun Microsystems, Inc. business.
* Permission to use, copy, modify, and distribute this
* software is freely granted, provided that this notice
* is preserved.
* ```
*/var t=-.16666666666666632,n=.00833333333332249,o=-.0001984126982985795,s=27557313707070068e-22,a=-25050760253406863e-24,i=158969099521155e-24;function l(u,c){var m,p,f,h;return h=u*u,f=h*h,m=n+h*(o+h*s)+h*f*(a+h*i),p=h*u,c===0?u+p*(t+h*m):u-(h*(.5*c-p*m)-c-p*t)}e.exports=l}}),tn=b({"node_modules/@stdlib/math-base-special-kernel-sin/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=Va();e.exports=t}}),Za=b({"node_modules/@stdlib/constants-float64-high-word-significand-mask/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=1048575;e.exports=t}}),Ka=b({"node_modules/@stdlib/number-float64-base-get-low-word/lib/low.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=Ge(),n;t===!0?n=0:n=1,e.exports=n}}),Ja=b({"node_modules/@stdlib/number-float64-base-get-low-word/lib/main.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=$e(),n=ze(),o=Ka(),s=new n(1),a=new t(s.buffer);function i(l){return s[0]=l,a[o]}e.exports=i}}),Qa=b({"node_modules/@stdlib/number-float64-base-get-low-word/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=Ja();e.exports=t}}),ei=b({"node_modules/@stdlib/number-float64-base-from-words/lib/indices.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=Ge(),n,o,s;t===!0?(o=1,s=0):(o=0,s=1),n={HIGH:o,LOW:s},e.exports=n}}),ri=b({"node_modules/@stdlib/number-float64-base-from-words/lib/main.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=$e(),n=ze(),o=ei(),s=new n(1),a=new t(s.buffer),i=o.HIGH,l=o.LOW;function u(c,m){return a[i]=c,a[l]=m,s[0]}e.exports=u}}),fr=b({"node_modules/@stdlib/number-float64-base-from-words/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=ri();e.exports=t}}),ti=b({"node_modules/@stdlib/math-base-special-floor/lib/main.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=Math.floor;e.exports=t}}),ni=b({"node_modules/@stdlib/math-base-special-floor/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=ti();e.exports=t}}),hr=b({"node_modules/@stdlib/constants-float64-pinf/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=Number.POSITIVE_INFINITY;e.exports=t}}),oi=b({"node_modules/@stdlib/number-ctor/lib/main.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/e.exports=Number}}),si=b({"node_modules/@stdlib/number-ctor/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=oi();e.exports=t}}),et=b({"node_modules/@stdlib/constants-float64-ninf/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=si(),n=t.NEGATIVE_INFINITY;e.exports=n}}),nn=b({"node_modules/@stdlib/constants-float64-exponent-bias/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=1023;e.exports=t}}),ai=b({"node_modules/@stdlib/constants-float64-max-base2-exponent/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=1023;e.exports=t}}),ii=b({"node_modules/@stdlib/constants-float64-max-base2-exponent-subnormal/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=-1023;e.exports=t}}),li=b({"node_modules/@stdlib/constants-float64-min-base2-exponent-subnormal/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=-1074;e.exports=t}}),ci=b({"node_modules/@stdlib/math-base-assert-is-nan/lib/main.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/function t(n){return n!==n}e.exports=t}}),We=b({"node_modules/@stdlib/math-base-assert-is-nan/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=ci();e.exports=t}}),ui=b({"node_modules/@stdlib/math-base-assert-is-infinite/lib/main.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=hr(),n=et();function o(s){return s===t||s===n}e.exports=o}}),br=b({"node_modules/@stdlib/math-base-assert-is-infinite/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=ui();e.exports=t}}),on=b({"node_modules/@stdlib/constants-float64-high-word-sign-mask/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2022 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=2147483648;e.exports=t}}),mi=b({"node_modules/@stdlib/utils-define-property/lib/define_property.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2021 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=typeof Object.defineProperty=="function"?Object.defineProperty:null;e.exports=t}}),pi=b({"node_modules/@stdlib/utils-define-property/lib/has_define_property_support.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2021 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=mi();function n(){try{return t({},"x",{}),!0}catch{return!1}}e.exports=n}}),di=b({"node_modules/@stdlib/utils-define-property/lib/builtin.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=Object.defineProperty;e.exports=t}}),sn=b({"node_modules/@stdlib/string-base-format-interpolate/lib/is_number.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2022 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/function t(n){return typeof n=="number"}e.exports=t}}),an=b({"node_modules/@stdlib/string-base-format-interpolate/lib/zero_pad.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2022 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/function t(s){return s[0]==="-"}function n(s){var a="",i;for(i=0;i<s;i++)a+="0";return a}function o(s,a,i){var l=!1,u=a-s.length;return u<0||(t(s)&&(l=!0,s=s.substr(1)),s=i?s+n(u):n(u)+s,l&&(s="-"+s)),s}e.exports=o}}),fi=b({"node_modules/@stdlib/string-base-format-interpolate/lib/format_integer.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2022 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=sn(),n=an(),o=String.prototype.toLowerCase,s=String.prototype.toUpperCase;function a(i){var l,u,c;switch(i.specifier){case"b":l=2;break;case"o":l=8;break;case"x":case"X":l=16;break;case"d":case"i":case"u":default:l=10;break}if(u=i.arg,c=parseInt(u,10),!isFinite(c)){if(!t(u))throw new Error("invalid integer. Value: "+u);c=0}return c<0&&(i.specifier==="u"||l!==10)&&(c=4294967295+c+1),c<0?(u=(-c).toString(l),i.precision&&(u=n(u,i.precision,i.padRight)),u="-"+u):(u=c.toString(l),!c&&!i.precision?u="":i.precision&&(u=n(u,i.precision,i.padRight)),i.sign&&(u=i.sign+u)),l===16&&(i.alternate&&(u="0x"+u),u=i.specifier===s.call(i.specifier)?s.call(u):o.call(u)),l===8&&i.alternate&&u.charAt(0)!=="0"&&(u="0"+u),u}e.exports=a}}),hi=b({"node_modules/@stdlib/string-base-format-interpolate/lib/is_string.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2022 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/function t(n){return typeof n=="string"}e.exports=t}}),bi=b({"node_modules/@stdlib/string-base-format-interpolate/lib/format_double.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2022 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=Math.abs,n=String.prototype.toLowerCase,o=String.prototype.toUpperCase,s=String.prototype.replace,a=/e\+(\d)$/,i=/e-(\d)$/,l=/^(\d+)$/,u=/^(\d+)e/,c=/\.0$/,m=/\.0*e/,p=/(\..*[^0])0*e/;function f(h,g){var d,v;switch(g.specifier){case"e":case"E":v=h.toExponential(g.precision);break;case"f":case"F":v=h.toFixed(g.precision);break;case"g":case"G":t(h)<1e-4?(d=g.precision,d>0&&(d-=1),v=h.toExponential(d)):v=h.toPrecision(g.precision),g.alternate||(v=s.call(v,p,"$1e"),v=s.call(v,m,"e"),v=s.call(v,c,""));break;default:throw new Error("invalid double notation. Value: "+g.specifier)}return v=s.call(v,a,"e+0$1"),v=s.call(v,i,"e-0$1"),g.alternate&&(v=s.call(v,l,"$1."),v=s.call(v,u,"$1.e")),h>=0&&g.sign&&(v=g.sign+v),v=g.specifier===o.call(g.specifier)?o.call(v):n.call(v),v}e.exports=f}}),gi=b({"node_modules/@stdlib/string-base-format-interpolate/lib/space_pad.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2022 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/function t(o){var s="",a;for(a=0;a<o;a++)s+=" ";return s}function n(o,s,a){var i=s-o.length;return i<0||(o=a?o+t(i):t(i)+o),o}e.exports=n}}),vi=b({"node_modules/@stdlib/string-base-format-interpolate/lib/main.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2022 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=fi(),n=hi(),o=sn(),s=bi(),a=gi(),i=an(),l=String.fromCharCode,u=Array.isArray;function c(f){return f!==f}function m(f){var h={};return h.specifier=f.specifier,h.precision=f.precision===void 0?1:f.precision,h.width=f.width,h.flags=f.flags||"",h.mapping=f.mapping,h}function p(f){var h,g,d,v,x,_,y,w,O,j;if(!u(f))throw new TypeError("invalid argument. First argument must be an array. Value: `"+f+"`.");for(_="",y=1,O=0;O<f.length;O++)if(d=f[O],n(d))_+=d;else{if(h=d.precision!==void 0,d=m(d),!d.specifier)throw new TypeError("invalid argument. Token is missing `specifier` property. Index: `"+O+"`. Value: `"+d+"`.");for(d.mapping&&(y=d.mapping),g=d.flags,j=0;j<g.length;j++)switch(v=g.charAt(j),v){case" ":d.sign=" ";break;case"+":d.sign="+";break;case"-":d.padRight=!0,d.padZeros=!1;break;case"0":d.padZeros=g.indexOf("-")<0;break;case"#":d.alternate=!0;break;default:throw new Error("invalid flag: "+v)}if(d.width==="*"){if(d.width=parseInt(arguments[y],10),y+=1,c(d.width))throw new TypeError("the argument for * width at position "+y+" is not a number. Value: `"+d.width+"`.");d.width<0&&(d.padRight=!0,d.width=-d.width)}if(h&&d.precision==="*"){if(d.precision=parseInt(arguments[y],10),y+=1,c(d.precision))throw new TypeError("the argument for * precision at position "+y+" is not a number. Value: `"+d.precision+"`.");d.precision<0&&(d.precision=1,h=!1)}switch(d.arg=arguments[y],d.specifier){case"b":case"o":case"x":case"X":case"d":case"i":case"u":h&&(d.padZeros=!1),d.arg=t(d);break;case"s":d.maxWidth=h?d.precision:-1,d.arg=String(d.arg);break;case"c":if(!c(d.arg)){if(x=parseInt(d.arg,10),x<0||x>127)throw new Error("invalid character code. Value: "+d.arg);d.arg=c(x)?String(d.arg):l(x)}break;case"e":case"E":case"f":case"F":case"g":case"G":if(h||(d.precision=6),w=parseFloat(d.arg),!isFinite(w)){if(!o(d.arg))throw new Error("invalid floating-point number. Value: "+_);w=d.arg,d.padZeros=!1}d.arg=s(w,d);break;default:throw new Error("invalid specifier: "+d.specifier)}d.maxWidth>=0&&d.arg.length>d.maxWidth&&(d.arg=d.arg.substring(0,d.maxWidth)),d.padZeros?d.arg=i(d.arg,d.width||d.precision,d.padRight):d.width&&(d.arg=a(d.arg,d.width,d.padRight)),_+=d.arg||"",y+=1}return _}e.exports=p}}),yi=b({"node_modules/@stdlib/string-base-format-interpolate/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2022 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=vi();e.exports=t}}),_i=b({"node_modules/@stdlib/string-base-format-tokenize/lib/main.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2022 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=/%(?:([1-9]\d*)\$)?([0 +\-#]*)(\*|\d+)?(?:(\.)(\*|\d+)?)?[hlL]?([%A-Za-z])/g;function n(s){var a={mapping:s[1]?parseInt(s[1],10):void 0,flags:s[2],width:s[3],precision:s[5],specifier:s[6]};return s[4]==="."&&s[5]===void 0&&(a.precision="1"),a}function o(s){var a,i,l,u;for(i=[],u=0,l=t.exec(s);l;)a=s.slice(u,t.lastIndex-l[0].length),a.length&&i.push(a),l[6]==="%"?i.push("%"):i.push(n(l)),u=t.lastIndex,l=t.exec(s);return a=s.slice(u),a.length&&i.push(a),i}e.exports=o}}),xi=b({"node_modules/@stdlib/string-base-format-tokenize/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2022 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=_i();e.exports=t}}),Si=b({"node_modules/@stdlib/string-format/lib/is_string.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2022 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/function t(n){return typeof n=="string"}e.exports=t}}),wi=b({"node_modules/@stdlib/string-format/lib/main.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2022 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=yi(),n=xi(),o=Si();function s(a){var i,l;if(!o(a))throw new TypeError(s("invalid argument. First argument must be a string. Value: `%s`.",a));for(i=[n(a)],l=1;l<arguments.length;l++)i.push(arguments[l]);return t.apply(null,i)}e.exports=s}}),Mi=b({"node_modules/@stdlib/string-format/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2022 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=wi();e.exports=t}}),Ci=b({"node_modules/@stdlib/utils-define-property/lib/polyfill.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=Mi(),n=Object.prototype,o=n.toString,s=n.__defineGetter__,a=n.__defineSetter__,i=n.__lookupGetter__,l=n.__lookupSetter__;function u(c,m,p){var f,h,g,d;if(typeof c!="object"||c===null||o.call(c)==="[object Array]")throw new TypeError(t("invalid argument. First argument must be an object. Value: `%s`.",c));if(typeof p!="object"||p===null||o.call(p)==="[object Array]")throw new TypeError(t("invalid argument. Property descriptor must be an object. Value: `%s`.",p));if(h="value"in p,h&&(i.call(c,m)||l.call(c,m)?(f=c.__proto__,c.__proto__=n,delete c[m],c[m]=p.value,c.__proto__=f):c[m]=p.value),g="get"in p,d="set"in p,h&&(g||d))throw new Error("invalid argument. Cannot specify one or more accessors and a value or writable attribute in the property descriptor.");return g&&s&&s.call(c,m,p.get),d&&a&&a.call(c,m,p.set),c}e.exports=u}}),Oi=b({"node_modules/@stdlib/utils-define-property/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=pi(),n=di(),o=Ci(),s;t()?s=n:s=o,e.exports=s}}),Ri=b({"node_modules/@stdlib/utils-define-nonenumerable-read-only-property/lib/main.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=Oi();function n(o,s,a){t(o,s,{configurable:!1,enumerable:!1,writable:!1,value:a})}e.exports=n}}),ln=b({"node_modules/@stdlib/utils-define-nonenumerable-read-only-property/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=Ri();e.exports=t}}),Ti=b({"node_modules/@stdlib/number-float64-base-to-words/lib/indices.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=Ge(),n,o,s;t===!0?(o=1,s=0):(o=0,s=1),n={HIGH:o,LOW:s},e.exports=n}}),cn=b({"node_modules/@stdlib/number-float64-base-to-words/lib/assign.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=$e(),n=ze(),o=Ti(),s=new n(1),a=new t(s.buffer),i=o.HIGH,l=o.LOW;function u(c,m,p,f){return s[0]=c,m[f]=a[i],m[f+p]=a[l],m}e.exports=u}}),Pi=b({"node_modules/@stdlib/number-float64-base-to-words/lib/main.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=cn();function n(o){return t(o,[0,0],1,0)}e.exports=n}}),rt=b({"node_modules/@stdlib/number-float64-base-to-words/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=ln(),n=Pi(),o=cn();t(n,"assign",o),e.exports=n}}),Ei=b({"node_modules/@stdlib/math-base-special-copysign/lib/main.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=on(),n=Be(),o=rt(),s=be(),a=fr(),i=[0,0];function l(u,c){var m,p;return o.assign(u,i,1,0),m=i[0],m&=n,p=s(c),p&=t,m|=p,a(m,i[1])}e.exports=l}}),un=b({"node_modules/@stdlib/math-base-special-copysign/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=Ei();e.exports=t}}),mn=b({"node_modules/@stdlib/constants-float64-smallest-normal/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=22250738585072014e-324;e.exports=t}}),ki=b({"node_modules/@stdlib/math-base-special-abs/lib/main.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2021 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/function t(n){return Math.abs(n)}e.exports=t}}),ji=b({"node_modules/@stdlib/math-base-special-abs/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=ki();e.exports=t}}),pn=b({"node_modules/@stdlib/number-float64-base-normalize/lib/assign.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=mn(),n=br(),o=We(),s=ji(),a=4503599627370496;function i(l,u,c,m){return o(l)||n(l)?(u[m]=l,u[m+c]=0,u):l!==0&&s(l)<t?(u[m]=l*a,u[m+c]=-52,u):(u[m]=l,u[m+c]=0,u)}e.exports=i}}),Ai=b({"node_modules/@stdlib/number-float64-base-normalize/lib/main.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=pn();function n(o){return t(o,[0,0],1,0)}e.exports=n}}),Ii=b({"node_modules/@stdlib/number-float64-base-normalize/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=ln(),n=Ai(),o=pn();t(n,"assign",o),e.exports=n}}),Ni=b({"node_modules/@stdlib/number-float64-base-exponent/lib/main.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=be(),n=pr(),o=nn();function s(a){var i=t(a);return i=(i&n)>>>20,i-o|0}e.exports=s}}),Li=b({"node_modules/@stdlib/number-float64-base-exponent/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=Ni();e.exports=t}}),qi=b({"node_modules/@stdlib/math-base-special-ldexp/lib/main.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=hr(),n=et(),o=nn(),s=ai(),a=ii(),i=li(),l=We(),u=br(),c=un(),m=Ii().assign,p=Li(),f=rt(),h=fr(),g=2220446049250313e-31,d=2148532223,v=[0,0],x=[0,0];function _(y,w){var O,j;return w===0||y===0||l(y)||u(y)?y:(m(y,v,1,0),y=v[0],w+=v[1],w+=p(y),w<i?c(0,y):w>s?y<0?n:t:(w<=a?(w+=52,j=g):j=1,f.assign(y,x,1,0),O=x[0],O&=d,O|=w+o<<20,j*h(O,x[1])))}e.exports=_}}),Hi=b({"node_modules/@stdlib/math-base-special-ldexp/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=qi();e.exports=t}}),Fi=b({"node_modules/@stdlib/array-base-filled/lib/main.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2021 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/function t(n,o){var s,a;for(s=[],a=0;a<o;a++)s.push(n);return s}e.exports=t}}),Di=b({"node_modules/@stdlib/array-base-filled/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2021 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=Fi();e.exports=t}}),Bi=b({"node_modules/@stdlib/array-base-zeros/lib/main.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2021 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=Di();function n(o){return t(0,o)}e.exports=n}}),$i=b({"node_modules/@stdlib/array-base-zeros/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2021 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=Bi();e.exports=t}}),zi=b({"node_modules/@stdlib/math-base-special-rempio2/lib/kernel_rempio2.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*
*
* ## Notice
*
* The following copyright and license were part of the original implementation available as part of [FreeBSD]{@link https://svnweb.freebsd.org/base/release/9.3.0/lib/msun/src/k_rem_pio2.c}. The implementation follows the original, but has been modified for JavaScript.
*
* ```text
* Copyright (C) 1993 by Sun Microsystems, Inc. All rights reserved.
*
* Developed at SunPro, a Sun Microsystems, Inc. business.
* Permission to use, copy, modify, and distribute this
* software is freely granted, provided that this notice
* is preserved.
* ```
*/var t=ni(),n=Hi(),o=$i(),s=[10680707,7228996,1387004,2578385,16069853,12639074,9804092,4427841,16666979,11263675,12935607,2387514,4345298,14681673,3074569,13734428,16653803,1880361,10960616,8533493,3062596,8710556,7349940,6258241,3772886,3769171,3798172,8675211,12450088,3874808,9961438,366607,15675153,9132554,7151469,3571407,2607881,12013382,4155038,6285869,7677882,13102053,15825725,473591,9065106,15363067,6271263,9264392,5636912,4652155,7056368,13614112,10155062,1944035,9527646,15080200,6658437,6231200,6832269,16767104,5075751,3212806,1398474,7579849,6349435,12618859],a=[1.570796251296997,7549789415861596e-23,5390302529957765e-30,3282003415807913e-37,1270655753080676e-44,12293330898111133e-52,27337005381646456e-60,21674168387780482e-67],i=16777216,l=5960464477539063e-23,u=o(20),c=o(20),m=o(20),p=o(20);function f(g,d,v,x,_,y,w,O,j){var T,M,E,L,S,I,P,q,A;for(L=y,A=x[v],q=v,S=0;q>0;S++)M=l*A|0,p[S]=A-i*M|0,A=x[q-1]+M,q-=1;if(A=n(A,_),A-=8*t(A*.125),P=A|0,A-=P,E=0,_>0?(S=p[v-1]>>24-_,P+=S,p[v-1]-=S<<24-_,E=p[v-1]>>23-_):_===0?E=p[v-1]>>23:A>=.5&&(E=2),E>0){for(P+=1,T=0,S=0;S<v;S++)q=p[S],T===0?q!==0&&(T=1,p[S]=16777216-q):p[S]=16777215-q;if(_>0)switch(_){case 1:p[v-1]&=8388607;break;case 2:p[v-1]&=4194303;break}E===2&&(A=1-A,T!==0&&(A-=n(1,_)))}if(A===0){for(q=0,S=v-1;S>=y;S--)q|=p[S];if(q===0){for(I=1;p[y-I]===0;I++);for(S=v+1;S<=v+I;S++){for(j[O+S]=s[w+S],M=0,q=0;q<=O;q++)M+=g[q]*j[O+(S-q)];x[S]=M}return v+=I,f(g,d,v,x,_,y,w,O,j)}for(v-=1,_-=24;p[v]===0;)v-=1,_-=24}else A=n(A,-_),A>=i?(M=l*A|0,p[v]=A-i*M|0,v+=1,_+=24,p[v]=M):p[v]=A|0;for(M=n(1,_),S=v;S>=0;S--)x[S]=M*p[S],M*=l;for(S=v;S>=0;S--){for(M=0,I=0;I<=L&&I<=v-S;I++)M+=a[I]*x[S+I];m[v-S]=M}for(M=0,S=v;S>=0;S--)M+=m[S];for(E===0?d[0]=M:d[0]=-M,M=m[0]-M,S=1;S<=v;S++)M+=m[S];return E===0?d[1]=M:d[1]=-M,P&7}function h(g,d,v,x){var _,y,w,O,j,T,M,E,L;for(y=4,O=x-1,w=(v-3)/24|0,w<0&&(w=0),T=v-24*(w+1),E=w-O,L=O+y,M=0;M<=L;M++)E<0?u[M]=0:u[M]=s[E],E+=1;for(M=0;M<=y;M++){for(_=0,E=0;E<=O;E++)_+=g[E]*u[O+(M-E)];c[M]=_}return j=y,f(g,d,j,c,T,y,w,O,u)}e.exports=h}}),Gi=b({"node_modules/@stdlib/math-base-special-round/lib/main.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=Math.round;e.exports=t}}),Wi=b({"node_modules/@stdlib/math-base-special-round/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=Gi();e.exports=t}}),Ui=b({"node_modules/@stdlib/math-base-special-rempio2/lib/rempio2_medium.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*
*
* ## Notice
*
* The following copyright and license were part of the original implementation available as part of [FreeBSD]{@link https://svnweb.freebsd.org/base/release/9.3.0/lib/msun/src/k_rem_pio2.c}. The implementation follows the original, but has been modified for JavaScript.
*
* ```text
* Copyright (C) 1993 by Sun Microsystems, Inc. All rights reserved.
*
* Developed at SunPro, a Sun Microsystems, Inc. business.
* Permission to use, copy, modify, and distribute this
* software is freely granted, provided that this notice
* is preserved.
* ```
*/var t=Wi(),n=be(),o=.6366197723675814,s=1.5707963267341256,a=6077100506506192e-26,i=6077100506303966e-26,l=20222662487959506e-37,u=20222662487111665e-37,c=84784276603689e-45,m=2047;function p(f,h,g){var d,v,x,_,y,w,O;return v=t(f*o),_=f-v*s,y=v*a,O=h>>20|0,g[0]=_-y,d=n(g[0]),w=O-(d>>20&m),w>16&&(x=_,y=v*i,_=x-y,y=v*l-(x-_-y),g[0]=_-y,d=n(g[0]),w=O-(d>>20&m),w>49&&(x=_,y=v*u,_=x-y,y=v*c-(x-_-y),g[0]=_-y)),g[1]=_-g[0]-y,v}e.exports=p}}),Xi=b({"node_modules/@stdlib/math-base-special-rempio2/lib/main.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*
*
* ## Notice
*
* The following copyright and license were part of the original implementation available as part of [FreeBSD]{@link https://svnweb.freebsd.org/base/release/9.3.0/lib/msun/src/e_rem_pio2.c}. The implementation follows the original, but has been modified for JavaScript.
*
* ```text
* Copyright (C) 1993 by Sun Microsystems, Inc. All rights reserved.
*
* Developed at SunPro, a Sun Microsystems, Inc. business.
* Permission to use, copy, modify, and distribute this
* software is freely granted, provided that this notice
* is preserved.
*
* Optimized by Bruce D. Evans.
* ```
*/var t=Be(),n=pr(),o=Za(),s=be(),a=Qa(),i=fr(),l=zi(),u=Ui(),c=0,m=16777216,p=1.5707963267341256,f=6077100506506192e-26,h=2*f,g=3*f,d=4*f,v=598523,x=1072243195,_=1073928572,y=1074752122,w=1074977148,O=1075183036,j=1075388923,T=1075594811,M=1094263291,E=[0,0,0],L=[0,0];function S(I,P){var q,A,Z,D,ne,J,pe,N;if(Z=s(I)|0,D=Z&t|0,D<=x)return P[0]=I,P[1]=0,0;if(D<=y)return(D&o)===v?u(I,D,P):D<=_?Z>0?(N=I-p,P[0]=N-f,P[1]=N-P[0]-f,1):(N=I+p,P[0]=N+f,P[1]=N-P[0]+f,-1):Z>0?(N=I-2*p,P[0]=N-h,P[1]=N-P[0]-h,2):(N=I+2*p,P[0]=N+h,P[1]=N-P[0]+h,-2);if(D<=T)return D<=O?D===w?u(I,D,P):Z>0?(N=I-3*p,P[0]=N-g,P[1]=N-P[0]-g,3):(N=I+3*p,P[0]=N+g,P[1]=N-P[0]+g,-3):D===j?u(I,D,P):Z>0?(N=I-4*p,P[0]=N-d,P[1]=N-P[0]-d,4):(N=I+4*p,P[0]=N+d,P[1]=N-P[0]+d,-4);if(D<M)return u(I,D,P);if(D>=n)return P[0]=NaN,P[1]=NaN,0;for(q=a(I),A=(D>>20)-1046,N=i(D-(A<<20|0),q),J=0;J<2;J++)E[J]=N|0,N=(N-E[J])*m;for(E[2]=N,ne=3;E[ne-1]===c;)ne-=1;return pe=l(E,L,A,ne,1),Z<0?(P[0]=-L[0],P[1]=-L[1],-pe):(P[0]=L[0],P[1]=L[1],pe)}e.exports=S}}),dn=b({"node_modules/@stdlib/math-base-special-rempio2/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=Xi();e.exports=t}}),Yi=b({"node_modules/@stdlib/math-base-special-sin/lib/main.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*
*
* ## Notice
*
* The following copyright, license, and long comment were part of the original implementation available as part of [FreeBSD]{@link https://svnweb.freebsd.org/base/release/9.3.0/lib/msun/src/s_sin.c}. The implementation follows the original, but has been modified for JavaScript.
*
* ```text
* Copyright (C) 1993 by Sun Microsystems, Inc. All rights reserved.
*
* Developed at SunPro, a Sun Microsystems, Inc. business.
* Permission to use, copy, modify, and distribute this
* software is freely granted, provided that this notice
* is preserved.
* ```
*/var t=Be(),n=pr(),o=be(),s=rn(),a=tn(),i=dn(),l=1072243195,u=1045430272,c=[0,0];function m(p){var f,h;if(f=o(p),f&=t,f<=l)return f<u?p:a(p,0);if(f>=n)return NaN;switch(h=i(p,c),h&3){case 0:return a(c[0],c[1]);case 1:return s(c[0],c[1]);case 2:return-a(c[0],c[1]);default:return-s(c[0],c[1])}}e.exports=m}}),Vi=b({"node_modules/@stdlib/math-base-special-sin/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=Yi();e.exports=t}}),Zi=b({"node_modules/@stdlib/math-base-special-cos/lib/main.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*
*
* ## Notice
*
* The following copyright, license, and long comment were part of the original implementation available as part of [FreeBSD]{@link https://svnweb.freebsd.org/base/release/9.3.0/lib/msun/src/s_cos.c}. The implementation follows the original, but has been modified for JavaScript.
*
* ```text
* Copyright (C) 1993 by Sun Microsystems, Inc. All rights reserved.
*
* Developed at SunPro, a Sun Microsystems, Inc. business.
* Permission to use, copy, modify, and distribute this
* software is freely granted, provided that this notice
* is preserved.
* ```
*/var t=be(),n=rn(),o=tn(),s=dn(),a=Be(),i=pr(),l=[0,0],u=1072243195,c=1044381696;function m(p){var f,h;if(f=t(p),f&=a,f<=u)return f<c?1:n(p,0);if(f>=i)return NaN;switch(h=s(p,l),h&3){case 0:return n(l[0],l[1]);case 1:return-o(l[0],l[1]);case 2:return-n(l[0],l[1]);default:return o(l[0],l[1])}}e.exports=m}}),Ki=b({"node_modules/@stdlib/math-base-special-cos/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=Zi();e.exports=t}}),Ji=b({"node_modules/@stdlib/number-float64-base-set-high-word/lib/high.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=Ge(),n;t===!0?n=1:n=0,e.exports=n}}),Qi=b({"node_modules/@stdlib/number-float64-base-set-high-word/lib/main.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=$e(),n=ze(),o=Ji(),s=new n(1),a=new t(s.buffer);function i(l,u){return s[0]=l,a[o]=u>>>0,s[0]}e.exports=i}}),el=b({"node_modules/@stdlib/number-float64-base-set-high-word/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=Qi();e.exports=t}}),rl=b({"node_modules/@stdlib/math-base-special-cbrt/lib/polyval_p.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2022 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/function t(n){return n===0?1.87595182427177:1.87595182427177+n*(-1.8849797954337717+n*(1.6214297201053545+n*(-.758397934778766+n*.14599619288661245)))}e.exports=t}}),tl=b({"node_modules/@stdlib/math-base-special-cbrt/lib/main.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*
*
* ## Notice
*
* The following copyright, license, and long comment were part of the original implementation available as part of [FreeBSD]{@link https://svnweb.freebsd.org/base/release/9.3.0/lib/msun/src/s_cbrt.c?view=markup}. The implementation follows the original, but has been modified for JavaScript.
*
* ```text
* Copyright (C) 1993 by Sun Microsystems, Inc. All rights reserved.
*
* Developed at SunPro, a Sun Microsystems, Inc. business.
* Permission to use, copy, modify, and distribute this
* software is freely granted, provided that this notice
* is preserved.
*
* Optimized by Bruce D. Evans.
* ```
*/var t=mn(),n=on(),o=Be(),s=be(),a=el(),i=br(),l=fr(),u=rt(),c=We(),m=rl(),p=4294967295,f=3221225472,h=0x40000000000000,g=2147483648,d=1,v=715094163,x=696219795,_=s(t),y=[0,0];function w(O){var j,T,M,E,L,S,I;return O===0||c(O)||i(O)?O:(T=s(O)>>>0,j=(T&n)>>>0,T&=o,T<_?(S=h*O,M=(s(S)&o)>>>0,M=(M/3>>>0)+x>>>0,S=l(j|M,0)):(S=0,M=(T/3>>>0)+v>>>0,S=a(S,j|M)),E=S*S*(S/O),S*=m(E),u.assign(S,y,1,0),y[1]&g?(y[0]+=d,y[1]&=~g):y[1]|=g,S=l(y[0]&p,y[1]&f),L=S*S,E=O/L,I=S+S,E=(E-S)/(I+E),S+=S*E,S)}e.exports=w}}),nl=b({"node_modules/@stdlib/math-base-special-cbrt/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=tl();e.exports=t}}),ol=b({"node_modules/@stdlib/number-float64-base-signbit/lib/main.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=be();function n(o){var s=t(o);return!!(s>>>31)}e.exports=n}}),sl=b({"node_modules/@stdlib/number-float64-base-signbit/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=ol();e.exports=t}}),al=b({"node_modules/@stdlib/constants-float64-half-pi/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=1.5707963267948966;e.exports=t}}),il=b({"node_modules/@stdlib/constants-float64-fourth-pi/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=.7853981633974483;e.exports=t}}),ll=b({"node_modules/@stdlib/math-base-special-atan/lib/polyval_p.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2022 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/function t(n){return n===0?-64.85021904942025:-64.85021904942025+n*(-122.88666844901361+n*(-75.00855792314705+n*(-16.157537187333652+n*-.8750608600031904)))}e.exports=t}}),cl=b({"node_modules/@stdlib/math-base-special-atan/lib/polyval_q.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2022 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/function t(n){return n===0?194.5506571482614:194.5506571482614+n*(485.3903996359137+n*(432.88106049129027+n*(165.02700983169885+n*(24.858464901423062+n*1))))}e.exports=t}}),ul=b({"node_modules/@stdlib/math-base-special-atan/lib/main.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*
*
* ## Notice
*
* The original C code, long comment, copyright, license, and constants are from [Cephes]{@link http://www.netlib.org/cephes}. The implementation follows the original, but has been modified for JavaScript.
*
* ```text
* Copyright 1984, 1995, 2000 by Stephen L. Moshier
*
* Some software in this archive may be from the book _Methods and Programs for Mathematical Functions_ (Prentice-Hall or Simon & Schuster International, 1989) or from the Cephes Mathematical Library, a commercial product. In either event, it is copyrighted by the author. What you see here may be used freely but it comes with no support or guarantee.
*
* Stephen L. Moshier
* moshier@na-net.ornl.gov
* ```
*/var t=We(),n=hr(),o=al(),s=il(),a=et(),i=ll(),l=cl(),u=6123233995736766e-32,c=2.414213562373095;function m(p){var f,h,g,d;return t(p)||p===0?p:p===n?o:p===a?-o:(p<0&&(h=!0,p=-p),f=0,p>c?(g=o,f=1,p=-(1/p)):p<=.66?g=0:(g=s,f=2,p=(p-1)/(p+1)),d=p*p,d=d*i(d)/l(d),d=p*d+p,f===2?d+=.5*u:f===1&&(d+=u),g+=d,h?-g:g)}e.exports=m}}),ml=b({"node_modules/@stdlib/math-base-special-atan/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=ul();e.exports=t}}),pl=b({"node_modules/@stdlib/constants-float64-pi/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=3.141592653589793;e.exports=t}}),dl=b({"node_modules/@stdlib/math-base-special-atan2/lib/main.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*
*
* ## Notice
*
* The original code, copyright and license are from [Go]{@link https://golang.org/src/math/atan2.go}. The implementation follows the original, but has been modified for JavaScript.
*
* ```text
* Copyright (c) 2009 The Go Authors. All rights reserved.
*
* Redistribution and use in source and binary forms, with or without
* modification, are permitted provided that the following conditions are
* met:
*
*    * Redistributions of source code must retain the above copyright
* notice, this list of conditions and the following disclaimer.
*    * Redistributions in binary form must reproduce the above
* copyright notice, this list of conditions and the following disclaimer
* in the documentation and/or other materials provided with the
* distribution.
*    * Neither the name of Google Inc. nor the names of its
* contributors may be used to endorse or promote products derived from
* this software without specific prior written permission.
*
* THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
* "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
* LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
* A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
* OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
* SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
* LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
* DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
* THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
* (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
* OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
* ```
*/var t=br(),n=un(),o=sl(),s=We(),a=ml(),i=hr(),l=pl();function u(c,m){var p;return s(m)||s(c)?NaN:t(m)?m===i?t(c)?n(l/4,c):n(0,c):t(c)?n(3*l/4,c):n(l,c):t(c)?n(l/2,c):c===0?m>=0&&!o(m)?n(0,c):n(l,c):m===0?n(l/2,c):(p=a(c/m),m<0?p<=0?p+l:p-l:p)}e.exports=u}}),fl=b({"node_modules/@stdlib/math-base-special-atan2/lib/index.js"(r,e){"use strict";/**
* @license Apache-2.0
*
* Copyright (c) 2018 The Stdlib Authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/var t=dl();e.exports=t}}),hl=mr(Vi(),1),bl=mr(Ki(),1),gl=mr(nl(),1),vl=mr(fl(),1),de=vl.default,ae=gl.default,$=bl.default,U=hl.default;var ie=r=>Object.freeze(r.map(e=>Object.freeze(e))),fn=ie([[.4123907992659595,.35758433938387796,.1804807884018343],[.21263900587151036,.7151686787677559,.07219231536073371],[.01933081871559185,.11919477979462599,.9505321522496606]]),hn=ie([[12831/3959,-329/214,-1974/3959],[-851781/878810,1648619/878810,36519/878810],[705/12673,-2585/12673,705/667]]),bn=ie([[608311/1250200,189793/714400,198249/1000160],[35783/156275,247089/357200,198249/2500400],[0/1,32229/714400,5220557/5000800]]),gn=ie([[446124/178915,-333277/357830,-72051/178915],[-14852/17905,63121/35810,423/17905],[11844/330415,-50337/660830,316169/330415]]),vn=ie([[1.0479297925449969,.022946870601609652,-.05019226628920524],[.02962780877005599,.9904344267538799,-.017073799063418826],[-.009243040646204504,.015055191490298152,.7518742814281371]]),yn=ie([[.955473421488075,-.02309845494876471,.06325924320057072],[-.0283697093338637,1.0099953980813041,.021041441191917323],[.012314014864481998,-.020507649298898964,1.330365926242124]]),_n=ie([[.819022437996703,.3619062600528904,-.1288737815209879],[.0329836539323885,.9292868615863434,.0361446663506424],[.0481771893596242,.2642395317527308,.6335478284694309]]),xn=ie([[.210454268309314,.7936177747023054,-.0040720430116193],[1.9779985324311684,-2.42859224204858,.450593709617411],[.0259040424655478,.7827717124575296,-.8086757549230774]]),Sn=ie([[1.2268798758459243,-.5578149944602171,.2813910456659647],[-.0405757452148008,1.112286803280317,-.0717110580655164],[-.0763729366746601,-.4214933324022432,1.5869240198367816]]),wn=ie([[1,.3963377773761749,.2158037573099136],[1,-.1055613458156586,-.0638541728258133],[1,-.0894841775298119,-1.2914855480194092]]);var gr=Ue,Pn=Object.freeze({id:"xyz-d65-css4@1",reference:"https://www.w3.org/TR/2026/CRD-css-color-4-20261008/#color-conversion-code",observer:"cie-1931-2deg",whitePoint:"D65",luminanceScale:"relative-white-y-1",adaptation:"linear-bradford",precision:"binary64"}),le=(r,e)=>r.map(t=>t[0]*e[0]+t[1]*e[1]+t[2]*e[2]),Mn=r=>Math.abs(r)<=.04045?r/12.92:Math.sign(r)*((Math.abs(r)+.055)/1.055)**2.4,Cn=r=>Math.abs(r)<=.0031308?12.92*r:Math.sign(r)*(1.055*Math.abs(r)**(1/2.4)-.055),En=r=>(r%360+360)%360,On=r=>le(xn,le(_n,r).map(gr.cbrt)),Rn=r=>le(Sn,le(wn,r).map(e=>e**3)),kn=([r,e,t])=>{let n=En(t)*Math.PI/180;return[r,e*gr.cos(n),e*gr.sin(n)]},jn=([r,e,t])=>{let n=Math.hypot(e,t);return[r,n,n===0?0:En(gr.atan2(t,e)*180/Math.PI)]};function yl(r,e){switch(r){case"xyz-d65":return[...e];case"xyz-d50":return le(yn,e);case"srgb":return le(fn,e.map(Mn));case"display-p3":return le(bn,e.map(Mn));case"oklab":return Rn(e);case"oklch":return Rn(kn(e))}}function _l(r,e){switch(r){case"xyz-d65":return[...e];case"xyz-d50":return le(vn,e);case"srgb":return le(hn,e).map(Cn);case"display-p3":return le(gn,e).map(Cn);case"oklab":return On(e);case"oklch":return jn(On(e))}}function Tn(r){if(!r.every(Number.isFinite))throw new RangeError("Conversion exceeded finite binary64 range");return r}function R(r,e){if(he(r),!ur.includes(e))throw new Pe("targetSpace","unsupported color space");let t;return r.colorSpace===e?t=[...r.components]:r.colorSpace==="oklab"&&e==="oklch"?t=jn(r.components):r.colorSpace==="oklch"&&e==="oklab"?t=kn(r.components):t=_l(e,Tn(yl(r.colorSpace,r.components))),{colorSpace:e,components:Tn(t),alpha:r.alpha}}var Xe=r=>R(r,"xyz-d65");function F(r,e){let t=r.length;Array.isArray(r[0])||(r=[r]),Array.isArray(e[0])||(e=e.map(a=>[a]));let n=e[0].length,o=e[0].map((a,i)=>e.map(l=>l[i])),s=r.map(a=>o.map(i=>{let l=0;if(!Array.isArray(a)){for(let u of i)l+=a*u;return l}for(let u=0;u<a.length;u++)l+=a[u]*(i[u]||0);return l}));return t===1&&(s=s[0]),n===1?s.map(a=>a[0]):s}function Qe(r){return ge(r)==="string"}function ge(r){return(Object.prototype.toString.call(r).match(/^\[object\s+(.*?)\]$/)[1]||"").toLowerCase()}function Rr(r,{precision:e,unit:t}){return ve(r)?"none":ko(r,e)+(t??"")}function ve(r){return Number.isNaN(r)||r instanceof Number&&r?.none}function z(r){return ve(r)?0:r}function ko(r,e){if(r===0)return 0;let t=~~r,n=0;t&&e&&(n=~~Math.log10(Math.abs(t))+1);let o=10**(e-n);return Math.floor(r*o+.5)/o}var xl={deg:1,grad:.9,rad:180/Math.PI,turn:360};function jo(r){if(!r)return;r=r.trim();let e=/^([a-z]+)\((.+?)\)$/i,t=/^-?[\d.]+$/,n=/%|deg|g?rad|turn$/,o=/\/?\s*(none|[-\w.]+(?:%|deg|g?rad|turn)?)/g,s=r.match(e);if(s){let a=[];return s[2].replace(o,(i,l)=>{let u=l.match(n),c=l;if(u){let m=u[0],p=c.slice(0,-m.length);m==="%"?(c=new Number(p/100),c.type="<percentage>"):(c=new Number(p*xl[m]),c.type="<angle>",c.unit=m)}else t.test(c)?(c=new Number(c),c.type="<number>"):c==="none"&&(c=new Number(NaN),c.none=!0);i.startsWith("/")&&(c=c instanceof Number?c:new Number(c),c.alpha=!0),typeof c=="object"&&c instanceof Number&&(c.raw=l),a.push(c)}),{name:s[1].toLowerCase(),rawName:s[1],rawArgs:s[2],args:a}}}function Ao(r){return r[r.length-1]}function Ze(r,e,t){return isNaN(r)?e:isNaN(e)?r:r+(e-r)*t}function Io(r,e,t){return(t-r)/(e-r)}function xt(r,e,t){return Ze(e[0],e[1],Io(r[0],r[1],t))}function No(r){return r.map(e=>e.split("|").map(t=>{t=t.trim();let n=t.match(/^(<[a-z]+>)\[(-?[.\d]+),\s*(-?[.\d]+)\]?$/);if(n){let o=new String(n[1]);return o.range=[+n[2],+n[3]],o}return t}))}function Lo(r,e,t){return Math.max(Math.min(t,e),r)}function kr(r,e){return Math.sign(r)===Math.sign(e)?r:-r}function ce(r,e){return kr(Math.abs(r)**e,r)}function St(r,e){return e===0?0:r/e}function qo(r,e,t=0,n=r.length){for(;t<n;){let o=t+n>>1;r[o]<e?t=o+1:n=o}return t}var Sl=Object.freeze({__proto__:null,bisectLeft:qo,clamp:Lo,copySign:kr,interpolate:Ze,interpolateInv:Io,isNone:ve,isString:Qe,last:Ao,mapRange:xt,multiplyMatrices:F,parseCoordGrammar:No,parseFunction:jo,serializeNumber:Rr,skipNone:z,spow:ce,toPrecision:ko,type:ge,zdiv:St}),pt=class{add(e,t,n){if(typeof arguments[0]!="string"){for(var e in arguments[0])this.add(e,arguments[0][e],arguments[1]);return}(Array.isArray(e)?e:[e]).forEach(function(o){this[o]=this[o]||[],t&&this[o][n?"unshift":"push"](t)},this)}run(e,t){this[e]=this[e]||[],this[e].forEach(function(n){n.call(t&&t.context?t.context:t,t)})}},ye=new pt,re={gamut_mapping:"css",precision:5,deltaE:"76",verbose:globalThis?.process?.env?.NODE_ENV?.toLowerCase()!=="test",warn:function(e){this.verbose&&globalThis?.console?.warn?.(e)}},V={D50:[.3457/.3585,1,(1-.3457-.3585)/.3585],D65:[.3127/.329,1,(1-.3127-.329)/.329]};function dt(r){return Array.isArray(r)?r:V[r]}function Tr(r,e,t,n={}){if(r=dt(r),e=dt(e),!r||!e)throw new TypeError(`Missing white point to convert ${r?"":"from"}${!r&&!e?"/":""}${e?"":"to"}`);if(r===e)return t;let o={W1:r,W2:e,XYZ:t,options:n};if(ye.run("chromatic-adaptation-start",o),o.M||(o.W1===V.D65&&o.W2===V.D50?o.M=[[1.0479297925449969,.022946870601609652,-.05019226628920524],[.02962780877005599,.9904344267538799,-.017073799063418826],[-.009243040646204504,.015055191490298152,.7518742814281371]]:o.W1===V.D50&&o.W2===V.D65&&(o.M=[[.955473421488075,-.02309845494876471,.06325924320057072],[-.0283697093338637,1.0099953980813041,.021041441191917323],[.012314014864481998,-.020507649298898964,1.330365926242124]])),ye.run("chromatic-adaptation-end",o),o.M)return F(o.M,o.XYZ);throw new TypeError("Only Bradford CAT with white points D50 and D65 supported for now.")}var wl=new Set(["<number>","<percentage>","<angle>"]);function An(r,e,t,n){return Object.entries(r.coords).map(([s,a],i)=>{let l=e.coordGrammar[i],u=n[i],c=u?.type,m;if(u.none?m=l.find(h=>wl.has(h)):m=l.find(h=>h==c),!m){let h=a.name||s;throw new TypeError(`${c??u.raw} not allowed for ${h} in ${t}()`)}let p=m.range;c==="<percentage>"&&(p||=[0,1]);let f=a.range||a.refRange;return p&&f&&(n[i]=xt(p,f,n[i])),m})}function Ho(r,{meta:e}={}){let t={str:String(r)?.trim()};if(ye.run("parse-start",t),t.color)return t.color;if(t.parsed=jo(t.str),t.parsed){let n=t.parsed.name;if(n==="color"){let o=t.parsed.args.shift(),s=o.startsWith("--")?o.substring(2):`--${o}`,a=[o,s],i=t.parsed.rawArgs.indexOf("/")>0?t.parsed.args.pop():1;for(let c of C.all){let m=c.getFormat("color");if(m&&(a.includes(m.id)||m.ids?.filter(p=>a.includes(p)).length)){let p=Object.keys(c.coords).map((h,g)=>t.parsed.args[g]||0),f;return m.coordGrammar&&(f=An(c,m,"color",p)),e&&Object.assign(e,{formatId:"color",types:f}),m.id.startsWith("--")&&!o.startsWith("--")&&re.warn(`${c.name} is a non-standard space and not currently supported in the CSS spec. Use prefixed color(${m.id}) instead of color(${o}).`),o.startsWith("--")&&!m.id.startsWith("--")&&re.warn(`${c.name} is a standard space and supported in the CSS spec. Use color(${m.id}) instead of prefixed color(${o}).`),{spaceId:c.id,coords:p,alpha:i}}}let l="",u=o in C.registry?o:s;if(u in C.registry){let c=C.registry[u].formats?.color?.id;c&&(l=`Did you mean color(${c})?`)}throw new TypeError(`Cannot parse color(${o}). `+(l||"Missing a plugin?"))}else for(let o of C.all){let s=o.getFormat(n);if(s&&s.type==="function"){let a=1;(s.lastAlpha||Ao(t.parsed.args).alpha)&&(a=t.parsed.args.pop());let i=t.parsed.args,l;return s.coordGrammar&&(l=An(o,s,n,i)),e&&Object.assign(e,{formatId:s.name,types:l}),{spaceId:o.id,coords:i,alpha:a}}}}else for(let n of C.all)for(let o in n.formats){let s=n.formats[o];if(s.type!=="custom"||s.test&&!s.test(t.str))continue;let a=s.parse(t.str);if(a)return a.alpha??=1,e&&(e.formatId=o),a}throw new TypeError(`Could not parse ${r} as a color. Missing a plugin?`)}function k(r){if(Array.isArray(r))return r.map(k);if(!r)throw new TypeError("Empty color reference");Qe(r)&&(r=Ho(r));let e=r.space||r.spaceId;return e instanceof C||(r.space=C.get(e)),r.alpha===void 0&&(r.alpha=1),r}var Ml=75e-6,C=class r{constructor(e){this.id=e.id,this.name=e.name,this.base=e.base?r.get(e.base):null,this.aliases=e.aliases,this.base&&(this.fromBase=e.fromBase,this.toBase=e.toBase);let t=e.coords??this.base.coords;for(let o in t)"name"in t[o]||(t[o].name=o);this.coords=t;let n=e.white??this.base.white??"D65";this.white=dt(n),this.formats=e.formats??{};for(let o in this.formats){let s=this.formats[o];s.type||="function",s.name||=o}this.formats.color?.id||(this.formats.color={...this.formats.color??{},id:e.cssId||this.id}),e.gamutSpace?this.gamutSpace=e.gamutSpace==="self"?this:r.get(e.gamutSpace):this.isPolar?this.gamutSpace=this.base:this.gamutSpace=this,this.gamutSpace.isUnbounded&&(this.inGamut=(o,s)=>!0),this.referred=e.referred,Object.defineProperty(this,"path",{value:Cl(this).reverse(),writable:!1,enumerable:!0,configurable:!0}),ye.run("colorspace-init-end",this)}inGamut(e,{epsilon:t=Ml}={}){if(!this.equals(this.gamutSpace))return e=this.to(this.gamutSpace,e),this.gamutSpace.inGamut(e,{epsilon:t});let n=Object.values(this.coords);return e.every((o,s)=>{let a=n[s];if(a.type!=="angle"&&a.range){if(Number.isNaN(o))return!0;let[i,l]=a.range;return(i===void 0||o>=i-t)&&(l===void 0||o<=l+t)}return!0})}get isUnbounded(){return Object.values(this.coords).every(e=>!("range"in e))}get cssId(){return this.formats?.color?.id||this.id}get isPolar(){for(let e in this.coords)if(this.coords[e].type==="angle")return!0;return!1}getFormat(e){if(typeof e=="object")return e=In(e,this),e;let t;return e==="default"?t=Object.values(this.formats)[0]:t=this.formats[e],t?(t=In(t,this),t):null}equals(e){return e?this===e||this.id===e||this.id===e.id:!1}to(e,t){if(arguments.length===1){let i=k(e);[e,t]=[i.space,i.coords]}if(e=r.get(e),this.equals(e))return t;t=t.map(i=>Number.isNaN(i)?0:i);let n=this.path,o=e.path,s,a;for(let i=0;i<n.length&&n[i].equals(o[i]);i++)s=n[i],a=i;if(!s)throw new Error(`Cannot convert between color spaces ${this} and ${e}: no connection space was found`);for(let i=n.length-1;i>a;i--)t=n[i].toBase(t);for(let i=a+1;i<o.length;i++)t=o[i].fromBase(t);return t}from(e,t){if(arguments.length===1){let n=k(e);[e,t]=[n.space,n.coords]}return e=r.get(e),e.to(this,t)}toString(){return`${this.name} (${this.id})`}getMinCoords(){let e=[];for(let t in this.coords){let n=this.coords[t],o=n.range||n.refRange;e.push(o?.min??0)}return e}static registry={};static get all(){return[...new Set(Object.values(r.registry))]}static register(e,t){if(arguments.length===1&&(t=arguments[0],e=t.id),t=this.get(t),this.registry[e]&&this.registry[e]!==t)throw new Error(`Duplicate color space registration: '${e}'`);if(this.registry[e]=t,arguments.length===1&&t.aliases)for(let n of t.aliases)this.register(n,t);return t}static get(e,...t){if(!e||e instanceof r)return e;if(ge(e)==="string"){let o=r.registry[e.toLowerCase()];if(!o)throw new TypeError(`No color space found with id = "${e}"`);return o}if(t.length)return r.get(...t);throw new TypeError(`${e} is not a valid color space`)}static resolveCoord(e,t){let n=ge(e),o,s;if(n==="string"?e.includes(".")?[o,s]=e.split("."):[o,s]=[,e]:Array.isArray(e)?[o,s]=e:(o=e.space,s=e.coordId),o=r.get(o),o||(o=t),!o)throw new TypeError(`Cannot resolve coordinate reference ${e}: No color space specified and relative references are not allowed here`);if(n=ge(s),n==="number"||n==="string"&&s>=0){let l=Object.entries(o.coords)[s];if(l)return{space:o,id:l[0],index:s,...l[1]}}o=r.get(o);let a=s.toLowerCase(),i=0;for(let l in o.coords){let u=o.coords[l];if(l.toLowerCase()===a||u.name?.toLowerCase()===a)return{space:o,id:l,index:i,...u};i++}throw new TypeError(`No "${s}" coordinate found in ${o.name}. Its coordinates are: ${Object.keys(o.coords).join(", ")}`)}static DEFAULT_FORMAT={type:"functions",name:"color"}};function Cl(r){let e=[r];for(let t=r;t=t.base;)e.push(t);return e}function In(r,{coords:e}={}){if(r.coords&&!r.coordGrammar){r.type||="function",r.name||="color",r.coordGrammar=No(r.coords);let t=Object.entries(e).map(([n,o],s)=>{let a=r.coordGrammar[s][0],i=o.range||o.refRange,l=a.range,u="";return a=="<percentage>"?(l=[0,100],u="%"):a=="<angle>"&&(u="deg"),{fromRange:i,toRange:l,suffix:u}});r.serializeCoords=(n,o)=>n.map((s,a)=>{let{fromRange:i,toRange:l,suffix:u}=t[a];return i&&l&&(s=xt(i,l,s)),s=Rr(s,{precision:o,unit:u}),s})}return r}var W=new C({id:"xyz-d65",name:"XYZ D65",coords:{x:{name:"X"},y:{name:"Y"},z:{name:"Z"}},white:"D65",formats:{color:{ids:["xyz-d65","xyz"]}},aliases:["xyz"]}),X=class extends C{constructor(e){e.coords||(e.coords={r:{range:[0,1],name:"Red"},g:{range:[0,1],name:"Green"},b:{range:[0,1],name:"Blue"}}),e.base||(e.base=W),e.toXYZ_M&&e.fromXYZ_M&&(e.toBase??=t=>{let n=F(e.toXYZ_M,t);return this.white!==this.base.white&&(n=Tr(this.white,this.base.white,n)),n},e.fromBase??=t=>(t=Tr(this.base.white,this.white,t),F(e.fromXYZ_M,t))),e.referred??="display",super(e)}};function er(r,e){return r=k(r),!e||r.space.equals(e)?r.coords.slice():(e=C.get(e),e.from(r))}function Q(r,e){r=k(r);let{space:t,index:n}=C.resolveCoord(e,r.space);return er(r,t)[n]}function wt(r,e,t){return r=k(r),e=C.get(e),r.coords=e.to(r.space,t),r}wt.returns="color";function fe(r,e,t){if(r=k(r),arguments.length===2&&ge(arguments[1])==="object"){let n=arguments[1];for(let o in n)fe(r,o,n[o])}else{typeof t=="function"&&(t=t(Q(r,e)));let{space:n,index:o}=C.resolveCoord(e,r.space),s=er(r,n);s[o]=t,wt(r,n,s)}return r}fe.returns="color";var Mt=new C({id:"xyz-d50",name:"XYZ D50",white:"D50",base:W,fromBase:r=>Tr(W.white,"D50",r),toBase:r=>Tr("D50",W.white,r)}),Ol=216/24389,Nn=24/116,vr=24389/27,tt=V.D50,ee=new C({id:"lab",name:"Lab",coords:{l:{refRange:[0,100],name:"Lightness"},a:{refRange:[-125,125]},b:{refRange:[-125,125]}},white:tt,base:Mt,fromBase(r){let t=r.map((n,o)=>n/tt[o]).map(n=>n>Ol?ae(n):(vr*n+16)/116);return[116*t[1]-16,500*(t[0]-t[1]),200*(t[1]-t[2])]},toBase(r){let e=[];return e[1]=(r[0]+16)/116,e[0]=r[1]/500+e[1],e[2]=e[1]-r[2]/200,[e[0]>Nn?Math.pow(e[0],3):(116*e[0]-16)/vr,r[0]>8?Math.pow((r[0]+16)/116,3):r[0]/vr,e[2]>Nn?Math.pow(e[2],3):(116*e[2]-16)/vr].map((n,o)=>n*tt[o])},formats:{lab:{coords:["<number> | <percentage>","<number> | <percentage>[-1,1]","<number> | <percentage>[-1,1]"]}}});function ue(r){return(r%360+360)%360}function Rl(r,e){if(r==="raw")return e;let[t,n]=e.map(ue),o=n-t;return r==="increasing"?o<0&&(n+=360):r==="decreasing"?o>0&&(t+=360):r==="longer"?-180<o&&o<180&&(o>0?t+=360:n+=360):r==="shorter"&&(o>180?t+=360:o<-180&&(n+=360)),[t,n]}var Ke=new C({id:"lch",name:"LCH",coords:{l:{refRange:[0,100],name:"Lightness"},c:{refRange:[0,150],name:"Chroma"},h:{refRange:[0,360],type:"angle",name:"Hue"}},base:ee,fromBase(r){let[e,t,n]=r,o,s=.02;return Math.abs(t)<s&&Math.abs(n)<s?o=NaN:o=de(n,t)*180/Math.PI,[e,Math.sqrt(t**2+n**2),ue(o)]},toBase(r){let[e,t,n]=r;return t<0&&(t=0),isNaN(n)&&(n=0),[e,t*$(n*Math.PI/180),t*U(n*Math.PI/180)]},formats:{lch:{coords:["<number> | <percentage>","<number> | <percentage>","<number> | <angle>"]}}}),Ln=25**7,Pr=Math.PI,qn=180/Pr,Ee=Pr/180;function Hn(r){let e=r*r;return e*e*e*r}function Fo(r,e,{kL:t=1,kC:n=1,kH:o=1}={}){[r,e]=k([r,e]);let[s,a,i]=ee.from(r),l=Ke.from(ee,[s,a,i])[1],[u,c,m]=ee.from(e),p=Ke.from(ee,[u,c,m])[1];l<0&&(l=0),p<0&&(p=0);let f=(l+p)/2,h=Hn(f),g=.5*(1-Math.sqrt(h/(h+Ln))),d=(1+g)*a,v=(1+g)*c,x=Math.sqrt(d**2+i**2),_=Math.sqrt(v**2+m**2),y=d===0&&i===0?0:de(i,d),w=v===0&&m===0?0:de(m,v);y<0&&(y+=2*Pr),w<0&&(w+=2*Pr),y*=qn,w*=qn;let O=u-s,j=_-x,T=w-y,M=y+w,E=Math.abs(T),L;x*_===0?L=0:E<=180?L=T:T>180?L=T-360:T<-180?L=T+360:re.warn("the unthinkable has happened");let S=2*Math.sqrt(_*x)*U(L*Ee/2),I=(s+u)/2,P=(x+_)/2,q=Hn(P),A;x*_===0?A=M:E<=180?A=M/2:M<360?A=(M+360)/2:A=(M-360)/2;let Z=(I-50)**2,D=1+.015*Z/Math.sqrt(20+Z),ne=1+.045*P,J=1;J-=.17*$((A-30)*Ee),J+=.24*$(2*A*Ee),J+=.32*$((3*A+6)*Ee),J-=.2*$((4*A-63)*Ee);let pe=1+.015*P*J,N=30*Math.exp(-1*((A-275)/25)**2),cr=2*Math.sqrt(q/(q+Ln)),De=-1*U(2*N*Ee)*cr,Te=(O/(t*D))**2;return Te+=(j/(n*ne))**2,Te+=(S/(o*pe))**2,Te+=De*(j/(n*ne))*(S/(o*pe)),Math.sqrt(Te)}var Tl=[[.819022437996703,.3619062600528904,-.1288737815209879],[.0329836539323885,.9292868615863434,.0361446663506424],[.0481771893596242,.2642395317527308,.6335478284694309]],Pl=[[1.2268798758459243,-.5578149944602171,.2813910456659647],[-.0405757452148008,1.112286803280317,-.0717110580655164],[-.0763729366746601,-.4214933324022432,1.5869240198367816]],El=[[.210454268309314,.7936177747023054,-.0040720430116193],[1.9779985324311684,-2.42859224204858,.450593709617411],[.0259040424655478,.7827717124575296,-.8086757549230774]],kl=[[1,.3963377773761749,.2158037573099136],[1,-.1055613458156586,-.0638541728258133],[1,-.0894841775298119,-1.2914855480194092]],Ie=new C({id:"oklab",name:"Oklab",coords:{l:{refRange:[0,1],name:"Lightness"},a:{refRange:[-.4,.4]},b:{refRange:[-.4,.4]}},white:"D65",base:W,fromBase(r){let t=F(Tl,r).map(n=>ae(n));return F(El,t)},toBase(r){let t=F(kl,r).map(n=>n**3);return F(Pl,t)},formats:{oklab:{coords:["<percentage> | <number>","<number> | <percentage>[-1,1]","<number> | <percentage>[-1,1]"]}}});function ft(r,e){[r,e]=k([r,e]);let[t,n,o]=Ie.from(r),[s,a,i]=Ie.from(e),l=t-s,u=n-a,c=o-i;return Math.sqrt(l**2+u**2+c**2)}var jl=75e-6;function Ce(r,e,{epsilon:t=jl}={}){r=k(r),e||(e=r.space),e=C.get(e);let n=r.coords;return e!==r.space&&(n=e.from(r)),e.inGamut(n,{epsilon:t})}function Ne(r){return{space:r.space,coords:r.coords.slice(),alpha:r.alpha}}function Do(r,e,t="lab"){t=C.get(t);let n=t.from(r),o=t.from(e);return Math.sqrt(n.reduce((s,a,i)=>{let l=o[i];return isNaN(a)||isNaN(l)?s:s+(l-a)**2},0))}function Al(r,e){return Do(r,e,"lab")}var Il=Math.PI,Fn=Il/180;function Nl(r,e,{l:t=2,c:n=1}={}){[r,e]=k([r,e]);let[o,s,a]=ee.from(r),[,i,l]=Ke.from(ee,[o,s,a]),[u,c,m]=ee.from(e),p=Ke.from(ee,[u,c,m])[1];i<0&&(i=0),p<0&&(p=0);let f=o-u,h=i-p,g=s-c,d=a-m,v=g**2+d**2-h**2,x=.511;o>=16&&(x=.040975*o/(1+.01765*o));let _=.0638*i/(1+.0131*i)+.638,y;Number.isNaN(l)&&(l=0),l>=164&&l<=345?y=.56+Math.abs(.2*$((l+168)*Fn)):y=.36+Math.abs(.4*$((l+35)*Fn));let w=Math.pow(i,4),O=Math.sqrt(w/(w+1900)),j=_*(O*y+1-O),T=(f/(t*x))**2;return T+=(h/(n*_))**2,T+=v/j**2,Math.sqrt(T)}var Dn=203,Ct=new C({id:"xyz-abs-d65",cssId:"--xyz-abs-d65",name:"Absolute XYZ D65",coords:{x:{refRange:[0,9504.7],name:"Xa"},y:{refRange:[0,1e4],name:"Ya"},z:{refRange:[0,10888.3],name:"Za"}},base:W,fromBase(r){return r.map(e=>Math.max(e*Dn,0))},toBase(r){return r.map(e=>Math.max(e/Dn,0))}}),yr=1.15,_r=.66,Bn=2610/2**14,Ll=2**14/2610,$n=3424/2**12,zn=2413/2**7,Gn=2392/2**7,ql=1.7*2523/2**5,Wn=2**5/(1.7*2523),xr=-.56,nt=16295499532821565e-27,Hl=[[.41478972,.579999,.014648],[-.20151,1.120649,.0531008],[-.0166008,.2648,.6684799]],Fl=[[1.9242264357876067,-1.0047923125953657,.037651404030618],[.35031676209499907,.7264811939316552,-.06538442294808501],[-.09098281098284752,-.3127282905230739,1.5227665613052603]],Dl=[[.5,.5,0],[3.524,-4.066708,.542708],[.199076,1.096799,-1.295875]],Bl=[[1,.1386050432715393,.05804731615611886],[.9999999999999999,-.1386050432715393,-.05804731615611886],[.9999999999999998,-.09601924202631895,-.8118918960560388]],Bo=new C({id:"jzazbz",name:"Jzazbz",coords:{jz:{refRange:[0,1],name:"Jz"},az:{refRange:[-.5,.5]},bz:{refRange:[-.5,.5]}},base:Ct,fromBase(r){let[e,t,n]=r,o=yr*e-(yr-1)*n,s=_r*t-(_r-1)*e,i=F(Hl,[o,s,n]).map(function(p){let f=$n+zn*(p/1e4)**Bn,h=1+Gn*(p/1e4)**Bn;return(f/h)**ql}),[l,u,c]=F(Dl,i);return[(1+xr)*l/(1+xr*l)-nt,u,c]},toBase(r){let[e,t,n]=r,o=(e+nt)/(1+xr-xr*(e+nt)),a=F(Bl,[o,t,n]).map(function(p){let f=$n-p**Wn,h=Gn*p**Wn-zn;return 1e4*(f/h)**Ll}),[i,l,u]=F(Fl,a),c=(i+(yr-1)*u)/yr,m=(l+(_r-1)*c)/_r;return[c,m,u]},formats:{color:{coords:["<number> | <percentage>","<number> | <percentage>[-1,1]","<number> | <percentage>[-1,1]"]}}}),ht=new C({id:"jzczhz",name:"JzCzHz",coords:{jz:{refRange:[0,1],name:"Jz"},cz:{refRange:[0,1],name:"Chroma"},hz:{refRange:[0,360],type:"angle",name:"Hue"}},base:Bo,fromBase(r){let[e,t,n]=r,o,s=2e-4;return Math.abs(t)<s&&Math.abs(n)<s?o=NaN:o=de(n,t)*180/Math.PI,[e,Math.sqrt(t**2+n**2),ue(o)]},toBase(r){return[r[0],r[1]*$(r[2]*Math.PI/180),r[1]*U(r[2]*Math.PI/180)]}});function $l(r,e){[r,e]=k([r,e]);let[t,n,o]=ht.from(r),[s,a,i]=ht.from(e),l=t-s,u=n-a;Number.isNaN(o)&&Number.isNaN(i)?(o=0,i=0):Number.isNaN(o)?o=i:Number.isNaN(i)&&(i=o);let c=o-i,m=2*Math.sqrt(n*a)*U(c/2*(Math.PI/180));return Math.sqrt(l**2+u**2+m**2)}var $o=3424/4096,zo=2413/128,Go=2392/128,Un=2610/16384,zl=2523/32,Gl=16384/2610,Xn=32/2523,Wl=[[.3592832590121217,.6976051147779502,-.035891593232029],[-.1920808463704993,1.100476797037432,.0753748658519118],[.0070797844607479,.0748396662186362,.8433265453898765]],Ul=[[2048/4096,2048/4096,0],[6610/4096,-13613/4096,7003/4096],[17933/4096,-17390/4096,-543/4096]],Xl=[[.9999999999999998,.0086090370379328,.111029625003026],[.9999999999999998,-.0086090370379328,-.1110296250030259],[.9999999999999998,.5600313357106791,-.3206271749873188]],Yl=[[2.0701522183894223,-1.3263473389671563,.2066510476294053],[.3647385209748072,.6805660249472273,-.0453045459220347],[-.0497472075358123,-.0492609666966131,1.1880659249923042]],bt=new C({id:"ictcp",name:"ICTCP",coords:{i:{refRange:[0,1],name:"I"},ct:{refRange:[-.5,.5],name:"CT"},cp:{refRange:[-.5,.5],name:"CP"}},base:Ct,fromBase(r){let e=F(Wl,r);return Vl(e)},toBase(r){let e=Zl(r);return F(Yl,e)}});function Vl(r){let e=r.map(function(t){let n=$o+zo*(t/1e4)**Un,o=1+Go*(t/1e4)**Un;return(n/o)**zl});return F(Ul,e)}function Zl(r){return F(Xl,r).map(function(n){let o=Math.max(n**Xn-$o,0),s=zo-Go*n**Xn;return 1e4*(o/s)**Gl})}function Kl(r,e){[r,e]=k([r,e]);let[t,n,o]=bt.from(r),[s,a,i]=bt.from(e);return 720*Math.sqrt((t-s)**2+.25*(n-a)**2+(o-i)**2)}var Jl=V.D65,Wo=.42,Yn=1/Wo,ot=2*Math.PI,Uo=[[.401288,.650173,-.051461],[-.250268,1.204414,.045854],[-.002079,.048952,.953127]],Ql=[[1.8620678550872327,-1.0112546305316843,.14918677544445175],[.38752654323613717,.6214474419314753,-.008973985167612518],[-.015841498849333856,-.03412293802851557,1.0499644368778496]],ec=[[460,451,288],[460,-891,-261],[460,-220,-6300]],rc={dark:[.8,.525,.8],dim:[.9,.59,.9],average:[1,.69,1]},Me={h:[20.14,90,164.25,237.53,380.14],e:[.8,.7,1,1.2,.8],H:[0,100,200,300,400]},tc=180/Math.PI,Vn=Math.PI/180;function Xo(r,e){return r.map(n=>{let o=ce(e*Math.abs(n)*.01,Wo);return 400*kr(o,n)/(o+27.13)})}function nc(r,e){let t=100/e*27.13**Yn;return r.map(n=>{let o=Math.abs(n);return kr(t*ce(o/(400-o),Yn),n)})}function oc(r){let e=ue(r);e<=Me.h[0]&&(e+=360);let t=qo(Me.h,e)-1,[n,o]=Me.h.slice(t,t+2),[s,a]=Me.e.slice(t,t+2),i=Me.H[t],l=(e-n)/s;return i+100*l/(l+(o-e)/a)}function sc(r){let e=(r%400+400)%400,t=Math.floor(.01*e);e=e%100;let[n,o]=Me.h.slice(t,t+2),[s,a]=Me.e.slice(t,t+2);return ue((e*(a*n-s*o)-100*n*a)/(e*(a-s)-100*a))}function Yo(r,e,t,n,o){let s={};s.discounting=o,s.refWhite=r,s.surround=n;let a=r.map(g=>g*100);s.la=e,s.yb=t;let i=a[1],l=F(Uo,a);n=rc[s.surround];let u=n[0];s.c=n[1],s.nc=n[2];let m=(1/(5*s.la+1))**4;s.fl=m*s.la+.1*(1-m)*(1-m)*ae(5*s.la),s.flRoot=s.fl**.25,s.n=s.yb/i,s.z=1.48+Math.sqrt(s.n),s.nbb=.725*s.n**-.2,s.ncb=s.nbb;let p=o?1:Math.max(Math.min(u*(1-1/3.6*Math.exp((-s.la-42)/92)),1),0);s.dRgb=l.map(g=>Ze(1,i/g,p)),s.dRgbInv=s.dRgb.map(g=>1/g);let f=l.map((g,d)=>g*s.dRgb[d]),h=Xo(f,s.fl);return s.aW=s.nbb*(2*h[0]+h[1]+.05*h[2]),s}var Zn=Yo(Jl,64/Math.PI*.2,20,"average",!1);function gt(r,e){if(!(r.J!==void 0^r.Q!==void 0))throw new Error("Conversion requires one and only one: 'J' or 'Q'");if(!(r.C!==void 0^r.M!==void 0^r.s!==void 0))throw new Error("Conversion requires one and only one: 'C', 'M' or 's'");if(!(r.h!==void 0^r.H!==void 0))throw new Error("Conversion requires one and only one: 'h' or 'H'");if(r.J===0||r.Q===0)return[0,0,0];let t=0;r.h!==void 0?t=ue(r.h)*Vn:t=sc(r.H)*Vn;let n=$(t),o=U(t),s=0;r.J!==void 0?s=ce(r.J,1/2)*.1:r.Q!==void 0&&(s=.25*e.c*r.Q/((e.aW+4)*e.flRoot));let a=0;r.C!==void 0?a=r.C/s:r.M!==void 0?a=r.M/e.flRoot/s:r.s!==void 0&&(a=4e-4*r.s**2*(e.aW+4)/e.c);let i=ce(a*Math.pow(1.64-Math.pow(.29,e.n),-.73),10/9),l=.25*($(t+2)+3.8),u=e.aW*ce(s,2/e.c/e.z),c=5e4/13*e.nc*e.ncb*l,m=u/e.nbb,p=23*(m+.305)*St(i,23*c+i*(11*n+108*o)),f=p*n,h=p*o,g=nc(F(ec,[m,f,h]).map(d=>d*1/1403),e.fl);return F(Ql,g.map((d,v)=>d*e.dRgbInv[v])).map(d=>d/100)}function Vo(r,e){let t=r.map(_=>_*100),n=Xo(F(Uo,t).map((_,y)=>_*e.dRgb[y]),e.fl),o=n[0]+(-12*n[1]+n[2])/11,s=(n[0]+n[1]-2*n[2])/9,a=(de(s,o)%ot+ot)%ot,i=.25*($(a+2)+3.8),l=5e4/13*e.nc*e.ncb*St(i*Math.sqrt(o**2+s**2),n[0]+n[1]+1.05*n[2]+.305),u=ce(l,.9)*Math.pow(1.64-Math.pow(.29,e.n),.73),c=e.nbb*(2*n[0]+n[1]+.05*n[2]),m=ce(c/e.aW,.5*e.c*e.z),p=100*ce(m,2),f=4/e.c*m*(e.aW+4)*e.flRoot,h=u*m,g=h*e.flRoot,d=ue(a*tc),v=oc(d),x=50*ce(e.c*u/(e.aW+4),1/2);return{J:p,C:h,h:d,s:x,Q:f,M:g,H:v}}var ac=new C({id:"cam16-jmh",cssId:"--cam16-jmh",name:"CAM16-JMh",coords:{j:{refRange:[0,100],name:"J"},m:{refRange:[0,105],name:"Colorfulness"},h:{refRange:[0,360],type:"angle",name:"Hue"}},base:W,fromBase(r){let e=Vo(r,Zn);return[e.J,e.M,e.h]},toBase(r){return gt({J:r[0],M:r[1],h:r[2]},Zn)}}),ic=V.D65,lc=216/24389,Zo=24389/27;function cc(r){return 116*(r>lc?ae(r):(Zo*r+16)/116)-16}function vt(r){return r>8?Math.pow((r+16)/116,3):r/Zo}function uc(r,e){let[t,n,o]=r,s=[],a=0;if(o===0)return[0,0,0];let i=vt(o);o>0?a=.00379058511492914*o**2+.608983189401032*o+.9155088574762233:a=9514440756550361e-21*o**2+.08693057439788597*o-21.928975842194614;let l=2e-12,u=15,c=0,m=1/0;for(;c<=u;){s=gt({J:a,C:n,h:t},e);let p=Math.abs(s[1]-i);if(p<m){if(p<=l)return s;m=p}a=a-(s[1]-i)*a/(2*s[1]),c+=1}return gt({J:a,C:n,h:t},e)}function mc(r,e){let t=cc(r[1]);if(t===0)return[0,0,0];let n=Vo(r,Ot);return[ue(n.h),n.C,t]}var Ot=Yo(ic,200/Math.PI*vt(50),vt(50)*100,"average",!1),Je=new C({id:"hct",name:"HCT",coords:{h:{refRange:[0,360],type:"angle",name:"Hue"},c:{refRange:[0,145],name:"Colorfulness"},t:{refRange:[0,100],name:"Tone"}},base:W,fromBase(r){return mc(r)},toBase(r){return uc(r,Ot)},formats:{color:{id:"--hct",coords:["<number> | <angle>","<percentage> | <number>","<percentage> | <number>"]}}}),pc=Math.PI/180,Kn=[1,.007,.0228];function Jn(r){r[1]<0&&(r=Je.fromBase(Je.toBase(r)));let e=Math.log(Math.max(1+Kn[2]*r[1]*Ot.flRoot,1))/Kn[2],t=r[0]*pc,n=e*$(t),o=e*U(t);return[r[2],n,o]}function dc(r,e){[r,e]=k([r,e]);let[t,n,o]=Jn(Je.from(r)),[s,a,i]=Jn(Je.from(e));return Math.sqrt((t-s)**2+(n-a)**2+(o-i)**2)}var Le={deltaE76:Al,deltaECMC:Nl,deltaE2000:Fo,deltaEJz:$l,deltaEITP:Kl,deltaEOK:ft,deltaEHCT:dc};function fc(r){let e=r?Math.floor(Math.log10(Math.abs(r))):0;return Math.max(parseFloat(`1e${e-2}`),1e-6)}var Qn={hct:{method:"hct.c",jnd:2,deltaEMethod:"hct",blackWhiteClamp:{}},"hct-tonal":{method:"hct.c",jnd:0,deltaEMethod:"hct",blackWhiteClamp:{channel:"hct.t",min:0,max:100}}};function _e(r,{method:e=re.gamut_mapping,space:t=void 0,deltaEMethod:n="",jnd:o=2,blackWhiteClamp:s={}}={}){if(r=k(r),Qe(arguments[1])?t=arguments[1]:t||(t=r.space),t=C.get(t),Ce(r,t,{epsilon:0}))return r;let a;if(e==="css")a=hc(r,{space:t});else{if(e!=="clip"&&!Ce(r,t)){Object.prototype.hasOwnProperty.call(Qn,e)&&({method:e,jnd:o,deltaEMethod:n,blackWhiteClamp:s}=Qn[e]);let i=Fo;if(n!==""){for(let u in Le)if("deltae"+n.toLowerCase()===u.toLowerCase()){i=Le[u];break}}let l=_e(H(r,t),{method:"clip",space:t});if(i(r,l)>o){if(Object.keys(s).length===3){let x=C.resolveCoord(s.channel),_=Q(H(r,x.space),x.id);if(ve(_)&&(_=0),_>=s.max)return H({space:"xyz-d65",coords:V.D65},r.space);if(_<=s.min)return H({space:"xyz-d65",coords:[0,0,0]},r.space)}let u=C.resolveCoord(e),c=u.space,m=u.id,p=H(r,c);p.coords.forEach((x,_)=>{ve(x)&&(p.coords[_]=0)});let h=(u.range||u.refRange)[0],g=fc(o),d=h,v=Q(p,m);for(;v-d>g;){let x=Ne(p);x=_e(x,{space:t,method:"clip"}),i(p,x)-o<g?d=Q(p,m):v=Q(p,m),fe(p,m,(d+v)/2)}a=H(p,t)}else a=l}else a=H(r,t);if(e==="clip"||!Ce(a,t,{epsilon:0})){let i=Object.values(t.coords).map(l=>l.range||[]);a.coords=a.coords.map((l,u)=>{let[c,m]=i[u];return c!==void 0&&(l=Math.max(c,l)),m!==void 0&&(l=Math.min(l,m)),l})}}return t!==r.space&&(a=H(a,r.space)),r.coords=a.coords,r}_e.returns="color";var eo={WHITE:{space:Ie,coords:[1,0,0]},BLACK:{space:Ie,coords:[0,0,0]}};function hc(r,{space:e}={}){r=k(r),e||(e=r.space),e=C.get(e);let o=C.get("oklch");if(e.isUnbounded)return H(r,e);let s=H(r,o),a=s.coords[0];if(a>=1){let h=H(eo.WHITE,e);return h.alpha=r.alpha,H(h,e)}if(a<=0){let h=H(eo.BLACK,e);return h.alpha=r.alpha,H(h,e)}if(Ce(s,e,{epsilon:0}))return H(s,e);function i(h){let g=H(h,e),d=Object.values(e.coords);return g.coords=g.coords.map((v,x)=>{if("range"in d[x]){let[_,y]=d[x].range;return Lo(_,v,y)}return v}),g}let l=0,u=s.coords[1],c=!0,m=Ne(s),p=i(m),f=ft(p,m);if(f<.02)return p;for(;u-l>1e-4;){let h=(l+u)/2;if(m.coords[1]=h,c&&Ce(m,e,{epsilon:0}))l=h;else if(p=i(m),f=ft(p,m),f<.02){if(.02-f<1e-4)break;c=!1,l=h}else u=h}return p}function H(r,e,{inGamut:t}={}){r=k(r),e=C.get(e);let n=e.from(r),o={space:e,coords:n,alpha:r.alpha};return t&&(o=_e(o,t===!0?void 0:t)),o}H.returns="color";function Ve(r,{precision:e=re.precision,format:t="default",inGamut:n=!0,...o}={}){let s;r=k(r);let a=t;t=r.space.getFormat(t)??r.space.getFormat("default")??C.DEFAULT_FORMAT;let i=r.coords.slice();if(n||=t.toGamut,n&&!Ce(r)&&(i=_e(Ne(r),n===!0?void 0:n).coords),t.type==="custom")if(o.precision=e,t.serialize)s=t.serialize(i,r.alpha,o);else throw new TypeError(`format ${a} can only be used to parse colors, not for serialization`);else{let l=t.name||"color";t.serializeCoords?i=t.serializeCoords(i,e):e!==null&&(i=i.map(p=>Rr(p,{precision:e})));let u=[...i];if(l==="color"){let p=t.id||t.ids?.[0]||r.space.id;u.unshift(p)}let c=r.alpha;e!==null&&(c=Rr(c,{precision:e}));let m=r.alpha>=1||t.noAlpha?"":`${t.commas?",":" /"} ${c}`;s=`${l}(${u.join(t.commas?", ":" ")}${m})`}return s}var bc=[[.6369580483012914,.14461690358620832,.1688809751641721],[.2627002120112671,.6779980715188708,.05930171646986196],[0,.028072693049087428,1.060985057710791]],gc=[[1.716651187971268,-.355670783776392,-.25336628137366],[-.666684351832489,1.616481236634939,.0157685458139111],[.017639857445311,-.042770613257809,.942103121235474]],jr=new X({id:"rec2020-linear",cssId:"--rec2020-linear",name:"Linear REC.2020",white:"D65",toXYZ_M:bc,fromXYZ_M:gc}),Sr=1.09929682680944,ro=.018053968510807,Ko=new X({id:"rec2020",name:"REC.2020",base:jr,toBase(r){return r.map(function(e){return e<ro*4.5?e/4.5:Math.pow((e+Sr-1)/Sr,1/.45)})},fromBase(r){return r.map(function(e){return e>=ro?Sr*Math.pow(e,.45)-(Sr-1):4.5*e})}}),vc=[[.4865709486482162,.26566769316909306,.1982172852343625],[.2289745640697488,.6917385218365064,.079286914093745],[0,.04511338185890264,1.043944368900976]],yc=[[2.493496911941425,-.9313836179191239,-.40271078445071684],[-.8294889695615747,1.7626640603183463,.023624685841943577],[.03584583024378447,-.07617238926804182,.9568845240076872]],Jo=new X({id:"p3-linear",cssId:"--display-p3-linear",name:"Linear P3",white:"D65",toXYZ_M:vc,fromXYZ_M:yc}),_c=[[.41239079926595934,.357584339383878,.1804807884018343],[.21263900587151027,.715168678767756,.07219231536073371],[.01933081871559182,.11919477979462598,.9505321522496607]],G=[[3.2409699419045226,-1.537383177570094,-.4986107602930034],[-.9692436362808796,1.8759675015077202,.04155505740717559],[.05563007969699366,-.20397695888897652,1.0569715142428786]],Qo=new X({id:"srgb-linear",name:"Linear sRGB",white:"D65",toXYZ_M:_c,fromXYZ_M:G}),to={aliceblue:[240/255,248/255,1],antiquewhite:[250/255,235/255,215/255],aqua:[0,1,1],aquamarine:[127/255,1,212/255],azure:[240/255,1,1],beige:[245/255,245/255,220/255],bisque:[1,228/255,196/255],black:[0,0,0],blanchedalmond:[1,235/255,205/255],blue:[0,0,1],blueviolet:[138/255,43/255,226/255],brown:[165/255,42/255,42/255],burlywood:[222/255,184/255,135/255],cadetblue:[95/255,158/255,160/255],chartreuse:[127/255,1,0],chocolate:[210/255,105/255,30/255],coral:[1,127/255,80/255],cornflowerblue:[100/255,149/255,237/255],cornsilk:[1,248/255,220/255],crimson:[220/255,20/255,60/255],cyan:[0,1,1],darkblue:[0,0,139/255],darkcyan:[0,139/255,139/255],darkgoldenrod:[184/255,134/255,11/255],darkgray:[169/255,169/255,169/255],darkgreen:[0,100/255,0],darkgrey:[169/255,169/255,169/255],darkkhaki:[189/255,183/255,107/255],darkmagenta:[139/255,0,139/255],darkolivegreen:[85/255,107/255,47/255],darkorange:[1,140/255,0],darkorchid:[153/255,50/255,204/255],darkred:[139/255,0,0],darksalmon:[233/255,150/255,122/255],darkseagreen:[143/255,188/255,143/255],darkslateblue:[72/255,61/255,139/255],darkslategray:[47/255,79/255,79/255],darkslategrey:[47/255,79/255,79/255],darkturquoise:[0,206/255,209/255],darkviolet:[148/255,0,211/255],deeppink:[1,20/255,147/255],deepskyblue:[0,191/255,1],dimgray:[105/255,105/255,105/255],dimgrey:[105/255,105/255,105/255],dodgerblue:[30/255,144/255,1],firebrick:[178/255,34/255,34/255],floralwhite:[1,250/255,240/255],forestgreen:[34/255,139/255,34/255],fuchsia:[1,0,1],gainsboro:[220/255,220/255,220/255],ghostwhite:[248/255,248/255,1],gold:[1,215/255,0],goldenrod:[218/255,165/255,32/255],gray:[128/255,128/255,128/255],green:[0,128/255,0],greenyellow:[173/255,1,47/255],grey:[128/255,128/255,128/255],honeydew:[240/255,1,240/255],hotpink:[1,105/255,180/255],indianred:[205/255,92/255,92/255],indigo:[75/255,0,130/255],ivory:[1,1,240/255],khaki:[240/255,230/255,140/255],lavender:[230/255,230/255,250/255],lavenderblush:[1,240/255,245/255],lawngreen:[124/255,252/255,0],lemonchiffon:[1,250/255,205/255],lightblue:[173/255,216/255,230/255],lightcoral:[240/255,128/255,128/255],lightcyan:[224/255,1,1],lightgoldenrodyellow:[250/255,250/255,210/255],lightgray:[211/255,211/255,211/255],lightgreen:[144/255,238/255,144/255],lightgrey:[211/255,211/255,211/255],lightpink:[1,182/255,193/255],lightsalmon:[1,160/255,122/255],lightseagreen:[32/255,178/255,170/255],lightskyblue:[135/255,206/255,250/255],lightslategray:[119/255,136/255,153/255],lightslategrey:[119/255,136/255,153/255],lightsteelblue:[176/255,196/255,222/255],lightyellow:[1,1,224/255],lime:[0,1,0],limegreen:[50/255,205/255,50/255],linen:[250/255,240/255,230/255],magenta:[1,0,1],maroon:[128/255,0,0],mediumaquamarine:[102/255,205/255,170/255],mediumblue:[0,0,205/255],mediumorchid:[186/255,85/255,211/255],mediumpurple:[147/255,112/255,219/255],mediumseagreen:[60/255,179/255,113/255],mediumslateblue:[123/255,104/255,238/255],mediumspringgreen:[0,250/255,154/255],mediumturquoise:[72/255,209/255,204/255],mediumvioletred:[199/255,21/255,133/255],midnightblue:[25/255,25/255,112/255],mintcream:[245/255,1,250/255],mistyrose:[1,228/255,225/255],moccasin:[1,228/255,181/255],navajowhite:[1,222/255,173/255],navy:[0,0,128/255],oldlace:[253/255,245/255,230/255],olive:[128/255,128/255,0],olivedrab:[107/255,142/255,35/255],orange:[1,165/255,0],orangered:[1,69/255,0],orchid:[218/255,112/255,214/255],palegoldenrod:[238/255,232/255,170/255],palegreen:[152/255,251/255,152/255],paleturquoise:[175/255,238/255,238/255],palevioletred:[219/255,112/255,147/255],papayawhip:[1,239/255,213/255],peachpuff:[1,218/255,185/255],peru:[205/255,133/255,63/255],pink:[1,192/255,203/255],plum:[221/255,160/255,221/255],powderblue:[176/255,224/255,230/255],purple:[128/255,0,128/255],rebeccapurple:[102/255,51/255,153/255],red:[1,0,0],rosybrown:[188/255,143/255,143/255],royalblue:[65/255,105/255,225/255],saddlebrown:[139/255,69/255,19/255],salmon:[250/255,128/255,114/255],sandybrown:[244/255,164/255,96/255],seagreen:[46/255,139/255,87/255],seashell:[1,245/255,238/255],sienna:[160/255,82/255,45/255],silver:[192/255,192/255,192/255],skyblue:[135/255,206/255,235/255],slateblue:[106/255,90/255,205/255],slategray:[112/255,128/255,144/255],slategrey:[112/255,128/255,144/255],snow:[1,250/255,250/255],springgreen:[0,1,127/255],steelblue:[70/255,130/255,180/255],tan:[210/255,180/255,140/255],teal:[0,128/255,128/255],thistle:[216/255,191/255,216/255],tomato:[1,99/255,71/255],turquoise:[64/255,224/255,208/255],violet:[238/255,130/255,238/255],wheat:[245/255,222/255,179/255],white:[1,1,1],whitesmoke:[245/255,245/255,245/255],yellow:[1,1,0],yellowgreen:[154/255,205/255,50/255]},no=Array(3).fill("<percentage> | <number>[0, 255]"),oo=Array(3).fill("<number>[0, 255]"),qe=new X({id:"srgb",name:"sRGB",base:Qo,fromBase:r=>r.map(e=>{let t=e<0?-1:1,n=e*t;return n>.0031308?t*(1.055*n**(1/2.4)-.055):12.92*e}),toBase:r=>r.map(e=>{let t=e<0?-1:1,n=e*t;return n<=.04045?e/12.92:t*((n+.055)/1.055)**2.4}),formats:{rgb:{coords:no},rgb_number:{name:"rgb",commas:!0,coords:oo,noAlpha:!0},color:{},rgba:{coords:no,commas:!0,lastAlpha:!0},rgba_number:{name:"rgba",commas:!0,coords:oo},hex:{type:"custom",toGamut:!0,test:r=>/^#([a-f0-9]{3,4}){1,2}$/i.test(r),parse(r){r.length<=5&&(r=r.replace(/[a-f0-9]/gi,"$&$&"));let e=[];return r.replace(/[a-f0-9]{2}/gi,t=>{e.push(parseInt(t,16)/255)}),{spaceId:"srgb",coords:e.slice(0,3),alpha:e.slice(3)[0]}},serialize:(r,e,{collapse:t=!0}={})=>{e<1&&r.push(e),r=r.map(s=>Math.round(s*255));let n=t&&r.every(s=>s%17===0);return"#"+r.map(s=>n?(s/17).toString(16):s.toString(16).padStart(2,"0")).join("")}},keyword:{type:"custom",test:r=>/^[a-z]+$/i.test(r),parse(r){r=r.toLowerCase();let e={spaceId:"srgb",coords:null,alpha:1};if(r==="transparent"?(e.coords=to.black,e.alpha=0):e.coords=to[r],e.coords)return e}}}}),es=new X({id:"p3",cssId:"display-p3",name:"P3",base:Jo,fromBase:qe.fromBase,toBase:qe.toBase});re.display_space=qe;var xc;if(typeof CSS<"u"&&CSS.supports)for(let r of[ee,Ko,es]){let e=r.getMinCoords(),n=Ve({space:r,coords:e,alpha:1});if(CSS.supports("color",n)){re.display_space=r;break}}function Sc(r,{space:e=re.display_space,...t}={}){let n=Ve(r,t);if(typeof CSS>"u"||CSS.supports("color",n)||!re.display_space)n=new String(n),n.color=r;else{let o=r;if((r.coords.some(ve)||ve(r.alpha))&&!(xc??=CSS.supports("color","hsl(none 50% 50%)"))&&(o=Ne(r),o.coords=o.coords.map(z),o.alpha=z(o.alpha),n=Ve(o,t),CSS.supports("color",n)))return n=new String(n),n.color=o,n;o=H(o,e),n=new String(Ve(o,t)),n.color=o}return n}function wc(r,e){return r=k(r),e=k(e),r.space===e.space&&r.alpha===e.alpha&&r.coords.every((t,n)=>t===e.coords[n])}function xe(r){return Q(r,[W,"y"])}function rs(r,e){fe(r,[W,"y"],e)}function Mc(r){Object.defineProperty(r.prototype,"luminance",{get(){return xe(this)},set(e){rs(this,e)}})}var Cc=Object.freeze({__proto__:null,getLuminance:xe,register:Mc,setLuminance:rs});function Oc(r,e){r=k(r),e=k(e);let t=Math.max(xe(r),0),n=Math.max(xe(e),0);return n>t&&([t,n]=[n,t]),(t+.05)/(n+.05)}var Rc=.56,Tc=.57,Pc=.62,Ec=.65,so=.022,kc=1.414,jc=.1,Ac=5e-4,Ic=1.14,ao=.027,Nc=1.14;function io(r){return r>=so?r:r+(so-r)**kc}function ke(r){let e=r<0?-1:1,t=Math.abs(r);return e*Math.pow(t,2.4)}function Lc(r,e){e=k(e),r=k(r);let t,n,o,s,a,i;e=H(e,"srgb"),[s,a,i]=e.coords;let l=ke(s)*.2126729+ke(a)*.7151522+ke(i)*.072175;r=H(r,"srgb"),[s,a,i]=r.coords;let u=ke(s)*.2126729+ke(a)*.7151522+ke(i)*.072175,c=io(l),m=io(u),p=m>c;return Math.abs(m-c)<Ac?n=0:p?(t=m**Rc-c**Tc,n=t*Ic):(t=m**Ec-c**Pc,n=t*Nc),Math.abs(n)<jc?o=0:n>0?o=n-ao:o=n+ao,o*100}function qc(r,e){r=k(r),e=k(e);let t=Math.max(xe(r),0),n=Math.max(xe(e),0);n>t&&([t,n]=[n,t]);let o=t+n;return o===0?0:(t-n)/o}var Hc=5e4;function Fc(r,e){r=k(r),e=k(e);let t=Math.max(xe(r),0),n=Math.max(xe(e),0);return n>t&&([t,n]=[n,t]),n===0?Hc:(t-n)/n}function Dc(r,e){r=k(r),e=k(e);let t=Q(r,[ee,"l"]),n=Q(e,[ee,"l"]);return Math.abs(t-n)}var Bc=216/24389,lo=24/116,wr=24389/27,st=V.D65,yt=new C({id:"lab-d65",name:"Lab D65",coords:{l:{refRange:[0,100],name:"Lightness"},a:{refRange:[-125,125]},b:{refRange:[-125,125]}},white:st,base:W,fromBase(r){let t=r.map((n,o)=>n/st[o]).map(n=>n>Bc?ae(n):(wr*n+16)/116);return[116*t[1]-16,500*(t[0]-t[1]),200*(t[1]-t[2])]},toBase(r){let e=[];return e[1]=(r[0]+16)/116,e[0]=r[1]/500+e[1],e[2]=e[1]-r[2]/200,[e[0]>lo?Math.pow(e[0],3):(116*e[0]-16)/wr,r[0]>8?Math.pow((r[0]+16)/116,3):r[0]/wr,e[2]>lo?Math.pow(e[2],3):(116*e[2]-16)/wr].map((n,o)=>n*st[o])},formats:{"lab-d65":{coords:["<number> | <percentage>","<number> | <percentage>[-1,1]","<number> | <percentage>[-1,1]"]}}}),at=Math.pow(5,.5)*.5+.5;function $c(r,e){r=k(r),e=k(e);let t=Q(r,[yt,"l"]),n=Q(e,[yt,"l"]),o=Math.abs(Math.pow(t,at)-Math.pow(n,at)),s=Math.pow(o,1/at)*Math.SQRT2-40;return s<7.5?0:s}var Or=Object.freeze({__proto__:null,contrastAPCA:Lc,contrastDeltaPhi:$c,contrastLstar:Dc,contrastMichelson:qc,contrastWCAG21:Oc,contrastWeber:Fc});function zc(r,e,t={}){Qe(t)&&(t={algorithm:t});let{algorithm:n,...o}=t;if(!n){let s=Object.keys(Or).map(a=>a.replace(/^contrast/,"")).join(", ");throw new TypeError(`contrast() function needs a contrast algorithm. Please specify one of: ${s}`)}r=k(r),e=k(e);for(let s in Or)if("contrast"+n.toLowerCase()===s.toLowerCase())return Or[s](r,e,o);throw new TypeError(`Unknown contrast algorithm: ${n}`)}function Ar(r){let[e,t,n]=er(r,W),o=e+15*t+3*n;return[4*e/o,9*t/o]}function ts(r){let[e,t,n]=er(r,W),o=e+t+n;return[e/o,t/o]}function Gc(r){Object.defineProperty(r.prototype,"uv",{get(){return Ar(this)}}),Object.defineProperty(r.prototype,"xy",{get(){return ts(this)}})}var Wc=Object.freeze({__proto__:null,register:Gc,uv:Ar,xy:ts});function Ye(r,e,t={}){Qe(t)&&(t={method:t});let{method:n=re.deltaE,...o}=t;for(let s in Le)if("deltae"+n.toLowerCase()===s.toLowerCase())return Le[s](r,e,o);throw new TypeError(`Unknown deltaE method: ${n}`)}function Uc(r,e=.25){let n=[C.get("oklch","lch"),"l"];return fe(r,n,o=>o*(1+e))}function Xc(r,e=.25){let n=[C.get("oklch","lch"),"l"];return fe(r,n,o=>o*(1-e))}var Yc=Object.freeze({__proto__:null,darken:Xc,lighten:Uc});function ns(r,e,t=.5,n={}){return[r,e]=[k(r),k(e)],ge(t)==="object"&&([t,n]=[.5,t]),rr(r,e,n)(t)}function os(r,e,t={}){let n;Rt(r)&&([n,t]=[r,e],[r,e]=n.rangeArgs.colors);let{maxDeltaE:o,deltaEMethod:s,steps:a=2,maxSteps:i=1e3,...l}=t;n||([r,e]=[k(r),k(e)],n=rr(r,e,l));let u=Ye(r,e),c=o>0?Math.max(a,Math.ceil(u/o)+1):a,m=[];if(i!==void 0&&(c=Math.min(c,i)),c===1)m=[{p:.5,color:n(.5)}];else{let p=1/(c-1);m=Array.from({length:c},(f,h)=>{let g=h*p;return{p:g,color:n(g)}})}if(o>0){let p=m.reduce((f,h,g)=>{if(g===0)return 0;let d=Ye(h.color,m[g-1].color,s);return Math.max(f,d)},0);for(;p>o;){p=0;for(let f=1;f<m.length&&m.length<i;f++){let h=m[f-1],g=m[f],d=(g.p+h.p)/2,v=n(d);p=Math.max(p,Ye(v,h.color),Ye(v,g.color)),m.splice(f,0,{p:d,color:n(d)}),f++}}}return m=m.map(p=>p.color),m}function rr(r,e,t={}){if(Rt(r)){let[l,u]=[r,e];return rr(...l.rangeArgs.colors,{...l.rangeArgs.options,...u})}let{space:n,outputSpace:o,progression:s,premultiplied:a}=t;r=k(r),e=k(e),r=Ne(r),e=Ne(e);let i={colors:[r,e],options:t};if(n?n=C.get(n):n=C.registry[re.interpolationSpace]||r.space,o=o?C.get(o):n,r=H(r,n),e=H(e,n),r=_e(r),e=_e(e),n.coords.h&&n.coords.h.type==="angle"){let l=t.hue=t.hue||"shorter",u=[n,"h"],[c,m]=[Q(r,u),Q(e,u)];isNaN(c)&&!isNaN(m)?c=m:isNaN(m)&&!isNaN(c)&&(m=c),[c,m]=Rl(l,[c,m]),fe(r,u,c),fe(e,u,m)}return a&&(r.coords=r.coords.map(l=>l*r.alpha),e.coords=e.coords.map(l=>l*e.alpha)),Object.assign(l=>{l=s?s(l):l;let u=r.coords.map((p,f)=>{let h=e.coords[f];return Ze(p,h,l)}),c=Ze(r.alpha,e.alpha,l),m={space:n,coords:u,alpha:c};return a&&(m.coords=m.coords.map(p=>p/c)),o!==n&&(m=H(m,o)),m},{rangeArgs:i})}function Rt(r){return ge(r)==="function"&&!!r.rangeArgs}re.interpolationSpace="lab";function Vc(r){r.defineFunction("mix",ns,{returns:"color"}),r.defineFunction("range",rr,{returns:"function<color>"}),r.defineFunction("steps",os,{returns:"array<color>"})}var Zc=Object.freeze({__proto__:null,isRange:Rt,mix:ns,range:rr,register:Vc,steps:os}),ss=new C({id:"hsl",name:"HSL",coords:{h:{refRange:[0,360],type:"angle",name:"Hue"},s:{range:[0,100],name:"Saturation"},l:{range:[0,100],name:"Lightness"}},base:qe,fromBase:r=>{let e=Math.max(...r),t=Math.min(...r),[n,o,s]=r,[a,i,l]=[NaN,0,(t+e)/2],u=e-t;if(u!==0){switch(i=l===0||l===1?0:(e-l)/Math.min(l,1-l),e){case n:a=(o-s)/u+(o<s?6:0);break;case o:a=(s-n)/u+2;break;case s:a=(n-o)/u+4}a=a*60}return i<0&&(a+=180,i=Math.abs(i)),a>=360&&(a-=360),[a,i*100,l*100]},toBase:r=>{let[e,t,n]=r;e=e%360,e<0&&(e+=360),t/=100,n/=100;function o(s){let a=(s+e/30)%12,i=t*Math.min(n,1-n);return n-i*Math.max(-1,Math.min(a-3,9-a,1))}return[o(0),o(8),o(4)]},formats:{hsl:{coords:["<number> | <angle>","<percentage>","<percentage>"]},hsla:{coords:["<number> | <angle>","<percentage>","<percentage>"],commas:!0,lastAlpha:!0}}}),as=new C({id:"hsv",name:"HSV",coords:{h:{refRange:[0,360],type:"angle",name:"Hue"},s:{range:[0,100],name:"Saturation"},v:{range:[0,100],name:"Value"}},base:ss,fromBase(r){let[e,t,n]=r;t/=100,n/=100;let o=n+t*Math.min(n,1-n);return[e,o===0?0:200*(1-n/o),100*o]},toBase(r){let[e,t,n]=r;t/=100,n/=100;let o=n*(1-t/2);return[e,o===0||o===1?0:(n-o)/Math.min(o,1-o)*100,o*100]},formats:{color:{id:"--hsv",coords:["<number> | <angle>","<percentage> | <number>","<percentage> | <number>"]}}}),Kc=new C({id:"hwb",name:"HWB",coords:{h:{refRange:[0,360],type:"angle",name:"Hue"},w:{range:[0,100],name:"Whiteness"},b:{range:[0,100],name:"Blackness"}},base:as,fromBase(r){let[e,t,n]=r;return[e,n*(100-t)/100,100-n]},toBase(r){let[e,t,n]=r;t/=100,n/=100;let o=t+n;if(o>=1){let i=t/o;return[e,0,i*100]}let s=1-n,a=s===0?0:1-t/s;return[e,a*100,s*100]},formats:{hwb:{coords:["<number> | <angle>","<percentage> | <number>","<percentage> | <number>"]}}}),Jc=[[.5766690429101305,.1855582379065463,.1882286462349947],[.29734497525053605,.6273635662554661,.07529145849399788],[.02703136138641234,.07068885253582723,.9913375368376388]],Qc=[[2.0415879038107465,-.5650069742788596,-.34473135077832956],[-.9692436362808795,1.8759675015077202,.04155505740717557],[.013444280632031142,-.11836239223101838,1.0151749943912054]],is=new X({id:"a98rgb-linear",cssId:"--a98-rgb-linear",name:"Linear Adobe\xAE 98 RGB compatible",white:"D65",toXYZ_M:Jc,fromXYZ_M:Qc}),e0=new X({id:"a98rgb",cssId:"a98-rgb",name:"Adobe\xAE 98 RGB compatible",base:is,toBase:r=>r.map(e=>Math.pow(Math.abs(e),563/256)*Math.sign(e)),fromBase:r=>r.map(e=>Math.pow(Math.abs(e),256/563)*Math.sign(e))}),r0=[[.7977666449006423,.13518129740053308,.0313477341283922],[.2880748288194013,.711835234241873,8993693872564e-17],[0,0,.8251046025104602]],t0=[[1.3457868816471583,-.25557208737979464,-.05110186497554526],[-.5446307051249019,1.5082477428451468,.02052744743642139],[0,0,1.2119675456389452]],ls=new X({id:"prophoto-linear",cssId:"--prophoto-rgb-linear",name:"Linear ProPhoto",white:"D50",base:Mt,toXYZ_M:r0,fromXYZ_M:t0}),n0=1/512,o0=16/512,s0=new X({id:"prophoto",cssId:"prophoto-rgb",name:"ProPhoto",base:ls,toBase(r){return r.map(e=>e<o0?e/16:e**1.8)},fromBase(r){return r.map(e=>e>=n0?e**(1/1.8):16*e)}}),a0=new C({id:"oklch",name:"Oklch",coords:{l:{refRange:[0,1],name:"Lightness"},c:{refRange:[0,.4],name:"Chroma"},h:{refRange:[0,360],type:"angle",name:"Hue"}},white:"D65",base:Ie,fromBase(r){let[e,t,n]=r,o,s=2e-4;return Math.abs(t)<s&&Math.abs(n)<s?o=NaN:o=de(n,t)*180/Math.PI,[e,Math.sqrt(t**2+n**2),ue(o)]},toBase(r){let[e,t,n]=r,o,s;return isNaN(n)?(o=0,s=0):(o=t*$(n*Math.PI/180),s=t*U(n*Math.PI/180)),[e,o,s]},formats:{oklch:{coords:["<percentage> | <number>","<number> | <percentage>[0,1]","<number> | <angle>"]}}}),cs=V.D65,i0=216/24389,co=24389/27,[uo,mo]=Ar({space:W,coords:cs}),us=new C({id:"luv",name:"Luv",coords:{l:{refRange:[0,100],name:"Lightness"},u:{refRange:[-215,215]},v:{refRange:[-215,215]}},white:cs,base:W,fromBase(r){let e=[z(r[0]),z(r[1]),z(r[2])],t=e[1],[n,o]=Ar({space:W,coords:e});if(!Number.isFinite(n)||!Number.isFinite(o))return[0,0,0];let s=t<=i0?co*t:116*ae(t)-16;return[s,13*s*(n-uo),13*s*(o-mo)]},toBase(r){let[e,t,n]=r;if(e===0||ve(e))return[0,0,0];t=z(t),n=z(n);let o=t/(13*e)+uo,s=n/(13*e)+mo,a=e<=8?e/co:Math.pow((e+16)/116,3);return[a*(9*o/(4*s)),a,a*((12-3*o-20*s)/(4*s))]},formats:{color:{id:"--luv",coords:["<number> | <percentage>","<number> | <percentage>[-1,1]","<number> | <percentage>[-1,1]"]}}}),Tt=new C({id:"lchuv",name:"LChuv",coords:{l:{refRange:[0,100],name:"Lightness"},c:{refRange:[0,220],name:"Chroma"},h:{refRange:[0,360],type:"angle",name:"Hue"}},base:us,fromBase(r){let[e,t,n]=r,o,s=.02;return Math.abs(t)<s&&Math.abs(n)<s?o=NaN:o=de(n,t)*180/Math.PI,[e,Math.sqrt(t**2+n**2),ue(o)]},toBase(r){let[e,t,n]=r;return t<0&&(t=0),isNaN(n)&&(n=0),[e,t*$(n*Math.PI/180),t*U(n*Math.PI/180)]},formats:{color:{id:"--lchuv",coords:["<number> | <percentage>","<number> | <percentage>","<number> | <angle>"]}}}),l0=216/24389,c0=24389/27,po=G[0][0],fo=G[0][1],it=G[0][2],ho=G[1][0],bo=G[1][1],lt=G[1][2],go=G[2][0],vo=G[2][1],ct=G[2][2];function je(r,e,t){let n=e/(U(t)-r*$(t));return n<0?1/0:n}function Er(r){let e=Math.pow(r+16,3)/1560896,t=e>l0?e:r/c0,n=t*(284517*po-94839*it),o=t*(838422*it+769860*fo+731718*po),s=t*(632260*it-126452*fo),a=t*(284517*ho-94839*lt),i=t*(838422*lt+769860*bo+731718*ho),l=t*(632260*lt-126452*bo),u=t*(284517*go-94839*ct),c=t*(838422*ct+769860*vo+731718*go),m=t*(632260*ct-126452*vo);return{r0s:n/s,r0i:o*r/s,r1s:n/(s+126452),r1i:(o-769860)*r/(s+126452),g0s:a/l,g0i:i*r/l,g1s:a/(l+126452),g1i:(i-769860)*r/(l+126452),b0s:u/m,b0i:c*r/m,b1s:u/(m+126452),b1i:(c-769860)*r/(m+126452)}}function yo(r,e){let t=e/360*Math.PI*2,n=je(r.r0s,r.r0i,t),o=je(r.r1s,r.r1i,t),s=je(r.g0s,r.g0i,t),a=je(r.g1s,r.g1i,t),i=je(r.b0s,r.b0i,t),l=je(r.b1s,r.b1i,t);return Math.min(n,o,s,a,i,l)}var u0=new C({id:"hsluv",name:"HSLuv",coords:{h:{refRange:[0,360],type:"angle",name:"Hue"},s:{range:[0,100],name:"Saturation"},l:{range:[0,100],name:"Lightness"}},base:Tt,gamutSpace:qe,fromBase(r){let[e,t,n]=[z(r[0]),z(r[1]),z(r[2])],o;if(e>99.9999999)o=0,e=100;else if(e<1e-8)o=0,e=0;else{let s=Er(e),a=yo(s,n);o=t/a*100}return[n,o,e]},toBase(r){let[e,t,n]=[z(r[0]),z(r[1]),z(r[2])],o;if(n>99.9999999)n=100,o=0;else if(n<1e-8)n=0,o=0;else{let s=Er(n);o=yo(s,e)/100*t}return[n,o,e]},formats:{color:{id:"--hsluv",coords:["<number> | <angle>","<percentage> | <number>","<percentage> | <number>"]}}});G[0][0];G[0][1];G[0][2];G[1][0];G[1][1];G[1][2];G[2][0];G[2][1];G[2][2];function Ae(r,e){return Math.abs(e)/Math.sqrt(Math.pow(r,2)+1)}function _o(r){let e=Ae(r.r0s,r.r0i),t=Ae(r.r1s,r.r1i),n=Ae(r.g0s,r.g0i),o=Ae(r.g1s,r.g1i),s=Ae(r.b0s,r.b0i),a=Ae(r.b1s,r.b1i);return Math.min(e,t,n,o,s,a)}var m0=new C({id:"hpluv",name:"HPLuv",coords:{h:{refRange:[0,360],type:"angle",name:"Hue"},s:{range:[0,100],name:"Saturation"},l:{range:[0,100],name:"Lightness"}},base:Tt,gamutSpace:"self",fromBase(r){let[e,t,n]=[z(r[0]),z(r[1]),z(r[2])],o;if(e>99.9999999)o=0,e=100;else if(e<1e-8)o=0,e=0;else{let s=Er(e),a=_o(s);o=t/a*100}return[n,o,e]},toBase(r){let[e,t,n]=[z(r[0]),z(r[1]),z(r[2])],o;if(n>99.9999999)n=100,o=0;else if(n<1e-8)n=0,o=0;else{let s=Er(n);o=_o(s)/100*t}return[n,o,e]},formats:{color:{id:"--hpluv",coords:["<number> | <angle>","<percentage> | <number>","<percentage> | <number>"]}}}),xo=203,So=2610/2**14,p0=2**14/2610,d0=2523/2**5,wo=2**5/2523,Mo=3424/2**12,Co=2413/2**7,Oo=2392/2**7,f0=new X({id:"rec2100pq",cssId:"rec2100-pq",name:"REC.2100-PQ",base:jr,toBase(r){return r.map(function(e){return(Math.max(e**wo-Mo,0)/(Co-Oo*e**wo))**p0*1e4/xo})},fromBase(r){return r.map(function(e){let t=Math.max(e*xo/1e4,0),n=Mo+Co*t**So,o=1+Oo*t**So;return(n/o)**d0})}}),Ro=.17883277,To=.28466892,Po=.55991073,ut=3.7743,h0=new X({id:"rec2100hlg",cssId:"rec2100-hlg",name:"REC.2100-HLG",referred:"scene",base:jr,toBase(r){return r.map(function(e){return e<=.5?e**2/3*ut:(Math.exp((e-Po)/Ro)+To)/12*ut})},fromBase(r){return r.map(function(e){return e/=ut,e<=1/12?Math.sqrt(3*e):Ro*Math.log(12*e-To)+Po})}}),ms={};ye.add("chromatic-adaptation-start",r=>{r.options.method&&(r.M=ps(r.W1,r.W2,r.options.method))});ye.add("chromatic-adaptation-end",r=>{r.M||(r.M=ps(r.W1,r.W2,r.options.method))});function Ir({id:r,toCone_M:e,fromCone_M:t}){ms[r]=arguments[0]}function ps(r,e,t="Bradford"){let n=ms[t],[o,s,a]=F(n.toCone_M,r),[i,l,u]=F(n.toCone_M,e),c=[[i/o,0,0],[0,l/s,0],[0,0,u/a]],m=F(c,n.toCone_M);return F(n.fromCone_M,m)}Ir({id:"von Kries",toCone_M:[[.40024,.7076,-.08081],[-.2263,1.16532,.0457],[0,0,.91822]],fromCone_M:[[1.8599363874558397,-1.1293816185800916,.21989740959619328],[.3611914362417676,.6388124632850422,-6370596838649899e-21],[0,0,1.0890636230968613]]});Ir({id:"Bradford",toCone_M:[[.8951,.2664,-.1614],[-.7502,1.7135,.0367],[.0389,-.0685,1.0296]],fromCone_M:[[.9869929054667121,-.14705425642099013,.15996265166373122],[.4323052697233945,.5183602715367774,.049291228212855594],[-.00852866457517732,.04004282165408486,.96848669578755]]});Ir({id:"CAT02",toCone_M:[[.7328,.4296,-.1624],[-.7036,1.6975,.0061],[.003,.0136,.9834]],fromCone_M:[[1.0961238208355142,-.27886900021828726,.18274517938277307],[.4543690419753592,.4735331543074117,.07209780371722911],[-.009627608738429355,-.00569803121611342,1.0153256399545427]]});Ir({id:"CAT16",toCone_M:[[.401288,.650173,-.051461],[-.250268,1.204414,.045854],[-.002079,.048952,.953127]],fromCone_M:[[1.862067855087233,-1.0112546305316845,.14918677544445172],[.3875265432361372,.6214474419314753,-.008973985167612521],[-.01584149884933386,-.03412293802851557,1.0499644368778496]]});Object.assign(V,{A:[1.0985,1,.35585],C:[.98074,1,1.18232],D55:[.95682,1,.92149],D75:[.94972,1,1.22638],E:[1,1,1],F2:[.99186,1,.67393],F7:[.95041,1,1.08747],F11:[1.00962,1,.6435]});V.ACES=[.32168/.33767,1,(1-.32168-.33767)/.33767];var b0=[[.6624541811085053,.13400420645643313,.1561876870049078],[.27222871678091454,.6740817658111484,.05368951740793705],[-.005574649490394108,.004060733528982826,1.0103391003129971]],g0=[[1.6410233796943257,-.32480329418479,-.23642469523761225],[-.6636628587229829,1.6153315916573379,.016756347685530137],[.011721894328375376,-.008284441996237409,.9883948585390215]],ds=new X({id:"acescg",cssId:"--acescg",name:"ACEScg",coords:{r:{range:[0,65504],name:"Red"},g:{range:[0,65504],name:"Green"},b:{range:[0,65504],name:"Blue"}},referred:"scene",white:V.ACES,toXYZ_M:b0,fromXYZ_M:g0}),Mr=2**-16,mt=-.35828683,Cr=(Math.log2(65504)+9.72)/17.52,v0=new X({id:"acescc",cssId:"--acescc",name:"ACEScc",coords:{r:{range:[mt,Cr],name:"Red"},g:{range:[mt,Cr],name:"Green"},b:{range:[mt,Cr],name:"Blue"}},referred:"scene",base:ds,toBase(r){let e=-.3013698630136986;return r.map(function(t){return t<=e?(2**(t*17.52-9.72)-Mr)*2:t<Cr?2**(t*17.52-9.72):65504})},fromBase(r){return r.map(function(e){return e<=0?(Math.log2(Mr)+9.72)/17.52:e<Mr?(Math.log2(Mr+e*.5)+9.72)/17.52:(Math.log2(e)+9.72)/17.52})}}),Eo=Object.freeze({__proto__:null,A98RGB:e0,A98RGB_Linear:is,ACEScc:v0,ACEScg:ds,CAM16_JMh:ac,HCT:Je,HPLuv:m0,HSL:ss,HSLuv:u0,HSV:as,HWB:Kc,ICTCP:bt,JzCzHz:ht,Jzazbz:Bo,LCH:Ke,LCHuv:Tt,Lab:ee,Lab_D65:yt,Luv:us,OKLCH:a0,OKLab:Ie,P3:es,P3_Linear:Jo,ProPhoto:s0,ProPhoto_Linear:ls,REC_2020:Ko,REC_2020_Linear:jr,REC_2100_HLG:h0,REC_2100_PQ:f0,XYZ_ABS_D65:Ct,XYZ_D50:Mt,XYZ_D65:W,sRGB:qe,sRGB_Linear:Qo}),Y=class r{constructor(...e){let t;e.length===1&&(t=k(e[0]));let n,o,s;t?(n=t.space||t.spaceId,o=t.coords,s=t.alpha):[n,o,s]=e,Object.defineProperty(this,"space",{value:C.get(n),writable:!1,enumerable:!0,configurable:!0}),this.coords=o?o.slice():[0,0,0],this.alpha=s>1||s===void 0?1:s<0?0:s;for(let a=0;a<this.coords.length;a++)this.coords[a]==="NaN"&&(this.coords[a]=NaN);for(let a in this.space.coords)Object.defineProperty(this,a,{get:()=>this.get(a),set:i=>this.set(a,i)})}get spaceId(){return this.space.id}clone(){return new r(this.space,this.coords,this.alpha)}toJSON(){return{spaceId:this.spaceId,coords:this.coords,alpha:this.alpha}}display(...e){let t=Sc(this,...e);return t.color=new r(t.color),t}static get(e,...t){return e instanceof r?e:new r(e,...t)}static defineFunction(e,t,n=t){let{instance:o=!0,returns:s}=n,a=function(...i){let l=t(...i);if(s==="color")l=r.get(l);else if(s==="function<color>"){let u=l;l=function(...c){let m=u(...c);return r.get(m)},Object.assign(l,u)}else s==="array<color>"&&(l=l.map(u=>r.get(u)));return l};e in r||(r[e]=a),o&&(r.prototype[e]=function(...i){return a(this,...i)})}static defineFunctions(e){for(let t in e)r.defineFunction(t,e[t],e[t])}static extend(e){if(e.register)e.register(r);else for(let t in e)r.defineFunction(t,e[t])}};Y.defineFunctions({get:Q,getAll:er,set:fe,setAll:wt,to:H,equals:wc,inGamut:Ce,toGamut:_e,distance:Do,toString:Ve});Object.assign(Y,{util:Sl,hooks:ye,WHITES:V,Space:C,spaces:C.registry,parse:Ho,defaults:re});for(let r of Object.keys(Eo))C.register(Eo[r]);for(let r in C.registry)_t(r,C.registry[r]);ye.add("colorspace-init-end",r=>{_t(r.id,r),r.aliases?.forEach(e=>{_t(e,r)})});function _t(r,e){let t=r.replace(/-/g,"_");Object.defineProperty(Y.prototype,t,{get(){let n=this.getAll(r);return typeof Proxy>"u"?n:new Proxy(n,{has:(o,s)=>{try{return C.resolveCoord([e,s]),!0}catch{}return Reflect.has(o,s)},get:(o,s,a)=>{if(s&&typeof s!="symbol"&&!(s in o)){let{index:i}=C.resolveCoord([e,s]);if(i>=0)return o[i]}return Reflect.get(o,s,a)},set:(o,s,a,i)=>{if(s&&typeof s!="symbol"&&!(s in o)||s>=0){let{index:l}=C.resolveCoord([e,s]);if(l>=0)return o[l]=a,this.setAll(r,o),!0}return Reflect.set(o,s,a,i)}})},set(n){this.setAll(r,n)},configurable:!0,enumerable:!0})}Y.extend(Le);Y.extend({deltaE:Ye});Object.assign(Y,{deltaEMethods:Le});Y.extend(Yc);Y.extend({contrast:zc});Y.extend(Wc);Y.extend(Cc);Y.extend(Zc);Y.extend(Or);var y0=Object.freeze(Array.from({length:37},(r,e)=>50+e*25)),Nr=r=>y0.filter(e=>(e-50)%r===0),fs=Object.freeze({lightnessMin:.12,lightnessMax:.985,chromaFalloff:1.5,samplingStep:25});function Et(r={}){if(!r||typeof r!="object"||Array.isArray(r))throw new TypeError("Recipe settings must be an object");for(let t of Object.keys(r))if(!Object.hasOwn(fs,t))throw new TypeError(`Unknown recipe setting: ${t}`);let e={...fs,...r};for(let t of Object.values(e))if(!Number.isFinite(t))throw new TypeError("Recipe settings must be finite numbers");if(e.lightnessMin<0||e.lightnessMax>1||e.lightnessMax-e.lightnessMin<.1)throw new RangeError("Lightness bounds must lie in [0,1] and be at least 0.1 apart");if(e.chromaFalloff<.2||e.chromaFalloff>5)throw new RangeError("Chroma falloff must lie in [0.2,5]");if(![25,50].includes(e.samplingStep))throw new RangeError("Sampling step must be 25 or 50");return e}var Pt=r=>({colorSpace:"oklch",components:r,alpha:1}),hs=r=>r.every(e=>e>=-1e-9&&e<=1+1e-9);function me(r,e){if(hs(R(r,e).components))return r;let[t,n,o]=r.components,s=0,a=n;for(let i=0;i<28;i++){let l=(s+a)/2;hs(R(Pt([t,l,o]),e).components)?s=l:a=l}return Pt([t,s,o])}function bs(r,e="srgb",t={}){let{lightnessMin:n,lightnessMax:o,chromaFalloff:s,samplingStep:a}=Et(t);if(he(r),r.alpha!==1)throw new RangeError("Tonal canvas requires opaque sources; alpha must be 1");if(!["srgb","display-p3"].includes(e))throw new TypeError("Unsupported ramp target");let[i,l,u]=R(r,"oklch").components;if(i<-1e-12||i>1+1e-12||l>1)throw new RangeError("Tonal recipe supports SDR OKLab L in [0,1] and chroma up to 1");let c=Math.max(n+.03,Math.min(o-.035,i)),m=Nr(a).map(p=>{let f=Math.abs(p-500)/450,h=p<500?c+(o-c)*f:c+(n-c)*f,g=l*(1-f**s),d=Pt([h,g,u]),v=me(d,e),x=R(v,e),_=x.components.map(y=>Math.max(0,Math.min(1,y)));return{stop:p,requested:d,resolved:v,target:x,mapped:v.components[1]<g-1e-8,css:`color(${e} ${_.join(" ")})`}});return{recipe:"anchored-oklch@1",target:e,settings:{lightnessMin:n,lightnessMax:o,chromaFalloff:s,samplingStep:a},stops:m,anchorAdjusted:c!==i||m.find(p=>p.stop===500).mapped}}var or={};Ut(or,{cuspLightness:()=>P0,okhslToOklch:()=>R0,oklchToOkhsl:()=>T0});function _0(r,e,t){let n=r+.3963377774*e+.2158037573*t,o=r-.1055613458*e-.0638541728*t,s=r-.0894841775*e-1.291485548*t,a=n*n*n,i=o*o*o,l=s*s*s;return[4.0767416621*a-3.3077115913*i+.2309699292*l,-1.2684380046*a+2.6097574011*i-.3413193965*l,-.0041960863*a-.7034186147*i+1.707614701*l]}var nr=.206,jt=.03,tr=(1+nr)/(1+jt),kt=r=>.5*(tr*r-nr+Math.sqrt((tr*r-nr)*(tr*r-nr)+4*jt*tr*r)),x0=r=>(r*r+nr*r)/(tr*(r+jt));function S0(r,e){let t,n,o,s,a,i,l,u;-1.88170328*r-.80936493*e>1?(t=1.19086277,n=1.76576728,o=.59662641,s=.75515197,a=.56771245,i=4.0767416621,l=-3.3077115913,u=.2309699292):1.81444104*r-1.19445276*e>1?(t=.73956515,n=-.45954404,o=.08285427,s=.1254107,a=.14503204,i=-1.2684380046,l=2.6097574011,u=-.3413193965):(t=1.35733652,n=-.00915799,o=-1.1513021,s=-.50559606,a=.00692167,i=-.0041960863,l=-.7034186147,u=1.707614701);let c=t+n*r+o*e+s*r*r+a*r*e,m=.3963377774*r+.2158037573*e,p=-.1055613458*r-.0638541728*e,f=-.0894841775*r-1.291485548*e,h=1+c*m,g=1+c*p,d=1+c*f,v=h*h*h,x=g*g*g,_=d*d*d,y=3*m*h*h,w=3*p*g*g,O=3*f*d*d,j=6*m*m*h,T=6*p*p*g,M=6*f*f*d,E=i*v+l*x+u*_,L=i*y+l*w+u*O,S=i*j+l*T+u*M;return c-E*L/(L*L-.5*E*S)}function Lr(r,e){let t=S0(r,e),n=_0(1,t*r,t*e),o=ae(1/Math.max(n[0],n[1],n[2]));return[o,o*t]}function w0(r,e,t,n,o,s){s||(s=Lr(r,e));let a;if((t-o)*s[1]-(s[0]-o)*n<=0)a=s[1]*o/(n*s[0]+s[1]*(o-t));else{a=s[1]*(o-1)/(n*(s[0]-1)+s[1]*(o-t));let i=t-o,l=n,u=.3963377774*r+.2158037573*e,c=-.1055613458*r-.0638541728*e,m=-.0894841775*r-1.291485548*e,p=i+l*u,f=i+l*c,h=i+l*m,g=o*(1-a)+a*t,d=a*n,v=g+d*u,x=g+d*c,_=g+d*m,y=v*v*v,w=x*x*x,O=_*_*_,j=3*p*v*v,T=3*f*x*x,M=3*h*_*_,E=6*p*p*v,L=6*f*f*x,S=6*h*h*_,I=4.0767416621*y-3.3077115913*w+.2309699292*O-1,P=4.0767416621*j-3.3077115913*T+.2309699292*M,q=4.0767416621*E-3.3077115913*L+.2309699292*S,A=P/(P*P-.5*I*q),Z=-I*A,D=-1.2684380046*y+2.6097574011*w-.3413193965*O-1,ne=-1.2684380046*j+2.6097574011*T-.3413193965*M,J=-1.2684380046*E+2.6097574011*L-.3413193965*S,pe=ne/(ne*ne-.5*D*J),N=-D*pe,cr=-.0041960863*y-.7034186147*w+1.707614701*O-1,De=-.0041960863*j-.7034186147*T+1.707614701*M,Te=-.0041960863*E-.7034186147*L+1.707614701*S,Wt=De/(De*De-.5*cr*Te),Xr=-cr*Wt;Z=A>=0?Z:1e5,N=pe>=0?N:1e5,Xr=Wt>=0?Xr:1e5,a+=Math.min(Z,N,Xr)}return a}function M0(r,e,t){return t||(t=Lr(r,e)),[t[1]/t[0],t[1]/(1-t[0])]}function C0(r,e){return .11516993+1/(7.4477897+4.1590124*e+r*(-2.19557347+1.75198401*e+r*(-2.13704948-10.02301043*e+r*(-4.24894561+5.38770819*e+4.69891013*r))))}function O0(r,e){return .11239642+1/(1.6132032-.68124379*e+r*(.40370612+.90148123*e+r*(-.27087943+.6122399*e+r*(.00299215-.45399568*e-.14661872*r))))}function gs(r,e,t){let n=Lr(e,t),o=w0(e,t,r,1,r,n),s=M0(e,t,n),a=o/Math.min(r*s[0],(1-r)*s[1]),i=r*C0(e,t),l=(1-r)*O0(e,t),u=.9*a*Math.sqrt(Math.sqrt(1/(1/(i*i*i*i)+1/(l*l*l*l)))),c=r*.4,m=(1-r)*.8;return[Math.sqrt(1/(1/(c*c)+1/(m*m))),u,o]}function R0(r,e,t){if(t<=0||t>=1)return[Math.max(0,Math.min(1,t)),0,r];let n=r*Math.PI/180,o=x0(t);if(e<=0)return[o,0,r];let[s,a,i]=gs(o,$(n),U(n)),l,u,c,m;return e<.8?(l=1.25*e,u=0,c=.8*s,m=1-c/a):(l=5*(e-.8),u=a,c=.2*a*a*1.25*1.25/s,m=1-c/(i-a)),[o,u+l*c/(1-m*l),r]}function T0([r,e,t]){if(r<=0||r>=1)return{h:t,s:0,l:Math.max(0,Math.min(1,r))};if(e<1e-7)return{h:t,s:0,l:kt(r)};let n=t*Math.PI/180,[o,s,a]=gs(r,$(n),U(n)),i;if(e<s){let l=.8*o,u=1-l/s;i=.8*e/(l+u*e)}else{let l=.2*s*s*1.25*1.25/o,u=1-l/(a-s);i=.8+.2*(e-s)/(l+u*(e-s))}return{h:t,s:Math.max(0,Math.min(1,i)),l:kt(r)}}function P0(r){let e=r*Math.PI/180;return kt(Lr($(e),U(e))[0])}var vs=Y,At=or,ys=r=>({colorSpace:"oklch",components:r,alpha:1}),It=r=>r.every(e=>Number.isFinite(e)&&e>=-1e-9&&e<=1+1e-9);function _s(r,e,t,n,o){let s=R(e,t);if(!It(s.components))throw new RangeError("Model gamut solver failed");return{stop:n,requested:r,resolved:e,target:s,mapped:o,css:`color(${t} ${s.components.map(a=>Math.max(0,Math.min(1,a))).join(" ")})`}}function oe(r){return new vs("xyz-d65",R(r,"xyz-d65").components).to("hct").coords}function te(r,e,t,n){if(t===0||t===100)return{resolved:ys([t===100?1:0,0,0]),mapped:e>1e-7};let o=l=>new vs("hct",[r,l,t]).to("xyz-d65").coords,s=l=>({colorSpace:"xyz-d65",components:o(l),alpha:1}),a=s(e),i=e;if(!It(R(a,n).components)){let l=0,u=e;for(let c=0;c<30;c++){let m=(l+u)/2;It(R(s(m),n).components)?l=m:u=m}i=l,a=s(i)}return{resolved:R(a,"oklch"),mapped:i<e-1e-7}}function E0(r,e,t,n){let{lightnessMin:o,lightnessMax:s,chromaFalloff:a,baseChroma:i}=n,[l,u]=oe(r),c=Number.isFinite(l)?l:0,m=e.components[1]<1e-7?0:u;return Nr(n.samplingStep).map(p=>{let f=100*(s-(s-o)*(p-50)/900),h=Math.abs(p-500)/450,g=m*(1-h**a)*i/100,d=te(c,g,f,t);return{..._s({colorSpace:"hct",components:[c,g,f],alpha:1},d.resolved,t,p,d.mapped),modelCoordinates:[c,g,f]}})}function k0(r,e,t){let{algorithm:n,lightnessMin:o,lightnessMax:s,chromaFalloff:a,baseChroma:i,vibrancy:l}=t,u=me(r,"srgb"),c=At.oklchToOkhsl(u.components),m=c.s<1e-7?c.l:At.cuspLightness(c.h),p=t.policy?.anchor==="cusp"?m:c.l,f=Math.max(o+.03,Math.min(s-.035,p));return Nr(t.samplingStep).map(h=>{let g=Math.abs(h-500)/450,d=n==="okhsl-peak@2"?.5*(m-c.l):n==="okhsl-perceptual@1"?l/100*.5*Math.sign(m-c.l):0,v=g+(h<500?d:-d)*g*(1-g),x=f+((h<500?s:o)-f)*v,_=c.s*(1-g**a)*i/100,y=At.okhslToOklch(c.h,_,x);t.policy?.chroma==="source-cap"&&(y[1]=Math.min(y[1],u.components[1]*i/100));let w=ys(y),O=me(w,"srgb"),j=me(O,e);return{..._s(w,j,e,h,j.components[1]<w.components[1]-1e-8),modelCoordinates:[c.h,_,x]}})}function xs(r,e,t){let n=R(r,"oklch"),o=t.algorithm==="hct-tone@1"?E0(r,n,e,t):k0(n,e,t),s=o.find(l=>l.stop===500).resolved.components,a=n.components,i=Math.hypot(s[0]-a[0],s[1]-a[1]);return{stops:o,anchorAdjusted:i>1e-6||a[1]>1e-7&&Math.abs((s[2]-a[2]+540)%360-180)>.001}}var j0=Ue;function B(r){let e=R(r,"xyz-d65").components[1];return e>216/24389?116*j0.cbrt(e)-16:e*24389/27}var Ss=r=>({colorSpace:"oklch",components:r,alpha:1}),Nt=r=>r.every(e=>Number.isFinite(e)&&e>=-1e-9&&e<=1+1e-9);function Se(r,e,t){if(!Number.isFinite(e)||e<0||e>100)throw new RangeError("Tone must be finite and within [0,100]");if(!["srgb","display-p3"].includes(t))throw new TypeError("Unsupported tone target");let[,n,o]=R(r,"oklch").components;function s(l){let u=0,c=1;for(let m=0;m<36;m++){let p=(u+c)/2;B(Ss([p,l,o]))<e?u=p:c=p}return Ss([(u+c)/2,l,o])}let a=s(n);if(!Nt(R(a,t).components)){let l=0,u=n;for(let c=0;c<28;c++){let m=(l+u)/2;Nt(R(s(m),t).components)?l=m:u=m}a=s(l)}let i=R(a,t);if(!Nt(i.components)||Math.abs(B(a)-e)>1e-5)throw new RangeError("Tone constraint could not be resolved");return{resolved:a,target:i,mapped:a.components[1]<n-1e-8,css:`color(${t} ${i.components.map(l=>Math.max(0,Math.min(1,l))).join(" ")})`}}function qr(r,e){let t=R(r,"oklab").components,n=e.map(c=>R(c.resolved,"oklab").components),o=(c,m)=>Math.hypot(...c.map((p,f)=>p-m[f])),s=e.map(c=>B(c.resolved)),a=n.slice(1).map((c,m)=>o(c,n[m])),i=e.filter(c=>c.toneTarget!==void 0).map(c=>Math.abs(B(c.resolved)-c.toneTarget)),l=R(r,"oklch").components,u=l[1]>1e-6?e.filter(c=>c.resolved.components[1]>1e-6).map(c=>Math.abs((c.resolved.components[2]-l[2]+540)%360-180)):[];return{maxToneError:i.length?Math.max(...i):null,maxOklchHueDrift:u.length?Math.max(...u):null,adjacentDistanceMin:Math.min(...a),adjacentDistanceMax:Math.max(...a),anchorDelta:o(t,n[e.findIndex(c=>c.stop===500)]),gamutReducedStops:e.filter(c=>c.mapped).length,toneMonotonic:s.every((c,m)=>!m||c<=s[m-1]+1e-6)}}var se="hct-hue-balance@1",A0=r=>Math.max(0,Math.min(1,r)),ws=r=>(r=A0(r),r*r*(3-2*r));function I0(r,e,t){let n=((r-100+540)%360+360)%360-180;return(.02+.98*Math.exp(-.5*(n/28)**2))*(1-ws((e-20)/55))*ws((t-1)/7)}function Oe(r,e){if(r.resolved.components[1]<1e-7)return r;let[t,n]=oe(r.resolved),o=B(r.resolved);if(!Number.isFinite(t)||o<=0||o>=100)return r;let s=I0(t,o,n);if(s<1e-12)return r;let a=[(t-12*s+360)%360,n*(1-.08*s),o],i=te(...a,e),l=R(i.resolved,e);return{...r,...i,target:l,mapped:r.mapped||i.mapped,postprocess:{recipe:se,weight:s,before:r.resolved,requested:{colorSpace:"hct",components:a,alpha:1}},css:`color(${e} ${l.components.map(u=>Math.max(0,Math.min(1,u))).join(" ")})`}}var N0=1e-8,L0=(r,e)=>Object.hasOwn(r?.sourcePolicies?.rules??{},e)?structuredClone(r.sourcePolicies.rules[e]):null;function Hr(r){Qr(r);let e=Object.create(null),t=Object.create(null),n=o=>{if(Object.hasOwn(e,o))return e[o];let s=r.colors[o],a=L0(r,o),i=structuredClone(s),l="authored";if(a){let u=R(n(a.family),"oklch"),c=R(s,"oklch"),m=u.components[1]>N0;i={colorSpace:"oklch",components:[c.components[0],c.components[1],m?u.components[2]:c.components[2]],alpha:s.alpha},l=m?"family":"authored-achromatic-fallback"}return e[o]=i,t[o]={policy:a?Vr:null,rule:a?structuredClone(a):null,hueOrigin:l,authored:structuredClone(s),effective:structuredClone(i),authoredReference:Xe(s),reference:Xe(i),dependencies:a?[a.family,...t[a.family].dependencies]:[]},i};return Object.keys(r.colors).forEach(n),{colors:e,traces:t}}function sr(r,e,t,n){n=Math.max(-1,Math.min(1,n));let o=n<0?(t?.light??0)*-n:(t?.dark??0)*n;if(!o)return r;let s=R(r.resolved,"oklch");if(s.components[1]<1e-7)return r;let a={...s,components:[s.components[0],s.components[1],((s.components[2]+o)%360+360)%360]},i=Se(a,B(r.resolved),e),l=R(i.resolved,e);return{...r,...i,requested:a,target:l,mapped:r.mapped||i.mapped,hueRotation:o,css:`color(${e} ${l.components.map(u=>Math.max(0,Math.min(1,u))).join(" ")})`}}var Lt=12.250030101522825,qt=96.88492823209958,q0=9,He=["brightest","brighter","bright","prime","dim","dimmer","dimmest"];function Ms(r){return Math.min(q0,Math.max(0,(qt-r)/3),Math.max(0,(r-Lt)/3))}var Ht=or;function H0(r){let e={colorSpace:"xyz-d65",components:[.9504559270516716,1,1.0890577507598784],alpha:1},t=r>8?((r+16)/116)**3:r*27/24389,n={...e,components:e.components.map(o=>o*t)};return{requested:n,fit:{resolved:R(n,"oklch"),mapped:!1}}}function F0(r,e,t){let n=r.s*e/100,o=0,s=1;for(let u=0;u<40;u++){let c=(o+s)/2,m={colorSpace:"oklch",components:Ht.okhslToOklch(r.h,n,c),alpha:1};B(m)<t?o=c:s=c}let a=[r.h,n,(o+s)/2],i={colorSpace:"oklch",components:Ht.okhslToOklch(...a),alpha:1},l=me(i,"srgb");return{requested:i,fit:{resolved:l,mapped:Math.abs(l.components[1]-i.components[1])>1e-8},coordinates:a}}function D0(r,e,t,n){let o=r.components[1]*e/100,s=r.components[2],a=0,i=1;for(let u=0;u<36;u++){let c=(a+i)/2;B({colorSpace:"oklch",components:[c,o,s],alpha:1})<t?a=c:i=c}let l={colorSpace:"oklch",components:[(a+i)/2,o,s],alpha:1};return{requested:l,fit:Se(l,t,n)}}function Fr(r,e,t,n,o=null){let s=B(r),a=Math.max(Lt,Math.min(qt,s)),i=Ms(a),l=R(r,"oklch"),u=n==="hct"?oe(r):null,c=n==="okhsl"?Ht.oklchToOkhsl(me(l,"srgb").components):null,m=(o??He).map((p,f)=>{let h=He[f]??String(f),g=o?o[f]:f===3?s:a+(3-f)*i,d;if(t===0||l.components[1]<1e-7)d=H0(g);else if(n==="hct"){let w=Number.isFinite(u[0])?u[0]:0,O=l.components[1]<1e-7?0:u[1]*t/100;d={requested:{colorSpace:"hct",components:[w,O,g],alpha:1},fit:te(w,O,g,e),coordinates:[w,O,g]}}else n==="okhsl"?d=F0(c,t,g):d=D0(l,t,g,e);let{requested:v,fit:x,coordinates:_}=d,y=R(x.resolved,e);return{stop:f+1,name:h,requested:v,...x,target:y,toneTarget:g,modelCoordinates:_,css:`color(${e} ${y.components.map(w=>Math.max(0,Math.min(1,w))).join(" ")})`}});return{stops:m,gap:i,widened:!1,distinct:new Set(m.map(p=>p.target.components.map(f=>Math.round(f*255)).join(","))).size===7}}var ar=(r,e)=>Math.hypot(...r.map((t,n)=>t-e[n])),Cs=({count:r,path:e},t)=>{let n=Math.max(0,Math.min(r-1,(t-2)/96*(r-1))),o=Math.min(r-2,Math.floor(n)),s=n-o;return e[o].lab.map((a,i)=>a+(e[o+1].lab[i]-a)*s)},Dr=(r,e,t,n)=>{let{count:o,path:s}=r,a=Cs(r,e),i=e;for(let l=n>0?Math.floor((e-2)/96*(o-1))+1:Math.ceil((e-2)/96*(o-1))-1;l>=0&&l<o;l+=n){let u=s[l].tone;if(ar(a,s[l].lab)>=t){let c=i,m=u;for(let p=0;p<24;p++){let f=(c+m)/2;ar(a,Cs(r,f))<t?c=f:m=f}return(c+m)/2}i=u}return null},Fe=(r,e,t)=>{let n=[e],o=e;for(let s=0;s<3;s++){if(o=Dr(r,o,t,1),o===null)return null;n.unshift(o)}o=e;for(let s=0;s<3;s++){if(o=Dr(r,o,t,-1),o===null)return null;n.push(o)}return n},Br=(r,e,t)=>{let{count:n,tones:o}=r;if(Fe(r,e,t))return e;let s=o.map(i=>!!Fe(r,i,t)),a=[];for(let i=0;i<n;i++)if(s[i]){let l=o[i]<e?1:-1,u=i+l;if(u>=0&&u<n&&s[u]&&Math.abs(o[u]-e)<Math.abs(o[i]-e))continue;let c=o[i],m=u>=0&&u<n?o[u]:e;(c-e)*(m-e)<0&&(m=e);for(let p=0;p<30&&Math.abs(c-m)>1e-7;p++){let f=(c+m)/2;Fe(r,f,t)?c=f:m=f}a.push(c)}return a.sort((i,l)=>Math.abs(i-e)-Math.abs(l-e)||i-l)[0]};var lr="model-prime@2",zr="model-prime@3",ir="model-prime@4",$r=.065,we=new Map,B0=128,Ft=(r,e)=>`color(${r} ${e.components.map(t=>Math.max(0,Math.min(1,t))).join(" ")})`,Os=r=>new Set(r.map(e=>e.target.components.map(t=>Math.round(t*255)).join(","))).size===7,Rs=(r,e)=>r>e?-(r-e)/Math.max(1e-9,98-e):(e-r)/Math.max(1e-9,e-2);function Ts(r,e,t,n,o,s,a=0,i=lr,l){let u=JSON.stringify([r.colorSpace,r.components,r.alpha,e,t,n,o?.light??0,o?.dark??0,s??"off",a,i,l]);if(we.has(u)){let m=we.get(u);return we.delete(u),we.set(u,m),structuredClone(m)}let c=(i===zr||i===ir)&&n==="hct"?G0(r,e,t,o,s,a,l,i===ir):V0(r,e,t,n,o,s,a);return we.set(u,structuredClone(c)),we.size>B0&&we.delete(we.keys().next().value),c}function $0(r,e,t){let n=r.toneTarget,o=.15*t/100*Math.max(0,Math.min(1,(100-n)/27,(n-2)/27)),s=R(r.resolved,"oklch").components[1];if(s<=o+1e-5)return r;let[a,i]=oe(r.resolved);if(!Number.isFinite(a)||i<=0)return r;let l=0,u=i,c=null;for(let p=0;p<12;p++){let f=(l+u)/2,h=te(a,f,n,e);R(h.resolved,"oklch").components[1]>o?u=f:(l=f,c=h)}c||(c=te(a,0,n,e));let m=R(c.resolved,e);return{...r,...c,target:m,mapped:!0,primeChromaBalance:{ceiling:o,before:s,after:R(c.resolved,"oklch").components[1]},css:Ft(e,m)}}function z0(r,e,t,n,o,s,a,i){let l=u=>{let c=sr(u,e,n,Rs(u.toneTarget,i));return o===se?Oe(c,e):c};return Fr(r,e,t,"hct",s).stops.map(l).map(u=>a?$0(u,e,t):u).map((u,c)=>{let m=R(u.resolved,e);return{...u,target:m,css:Ft(e,m),name:He[c],stop:c+1}})}function G0(r,e,t,n,o,s,{lightnessMin:a=.05,lightnessMax:i=1}={},l=!1){let u=B(r),c=50*(a+i),m=Math.max(2,Math.min(8,100*(i-a)/12)),p=c+s*m,f=Math.max(2+3*m,Math.min(98-3*m,p)),h=Array.from({length:7},(y,w)=>f+(3-w)*m),g=z0(r,e,t,n,o,h,l,u),d=g.map(y=>R(y.resolved,"oklab").components),v=d.slice(1).map((y,w)=>ar(d[w],y)),x=g.map(y=>B(y.resolved)),_=x.slice(1).map((y,w)=>x[w]-y);return{stops:g,brightnessPolicy:s?"prime-brightness@1":void 0,brightnessSteps:s,unbiasedCenterTone:c,requestedCenterTone:p,brightnessLimited:Math.abs(f-p)>1e-6,gap:m,metric:"cielab-tone",chromaPolicy:l?"shared-prime-chroma-envelope@1":void 0,requestedGap:m,actualDistances:v,toneGaps:_,sourceTone:u,centerTone:f,centerAdjusted:Math.abs(f-u)>1e-6,compressed:!1,widened:!1,toneMonotonic:x.every((y,w)=>!w||y<x[w-1]),distinct:Os(g),spacingError:Math.max(..._.map(y=>Math.abs(y-m))),reason:Math.abs(f-p)>1e-6?"brightness-limited-by-seven-step-capacity":l?"shared-hct-tone-and-chroma-envelope":"shared-hct-tone-schedule"}}function W0(r,e,t){let n=Math.max(2,Math.min(98,e)),o=[n,...r.tones].sort((l,u)=>Math.abs(l-n)-Math.abs(u-n)||l-u),s=$r,a=Br(r,n,s);if(a===void 0){let l=0,u=s;for(let c=0;c<22;c++){let m=(l+u)/2;o.some(p=>Fe(r,p,m))?l=m:u=m}s=l,a=Br(r,n,s)}let i=a;if(t){n=a;for(let l=0;l<t;l++)n=Dr(r,n,s,1)??98;a=Br(r,n,s)}return{gap:s,center:a,wanted:n,unbiasedCenterTone:i}}function U0(r,e,t,n,o){return r?e?"brightness-limited-by-seven-step-capacity":"brightness-bias":t<$r-1e-6?"gamut-trajectory-capacity":Math.abs(n-o)>1e-6?"center-moved-for-seven-steps":null}function X0(r,{wanted:e,unbiasedCenterTone:t},n){return r?{brightnessPolicy:"prime-brightness@1",brightnessSteps:r,unbiasedCenterTone:t,requestedCenterTone:e,brightnessLimited:Math.abs(n-e)>1e-6}:{}}function Y0(r,e,t,n,o,s){return Fr(r,e,t,n,o).stops.map(s).map((a,i)=>({...a,target:R(a.resolved,e),css:Ft(e,R(a.resolved,e)),name:He[i],stop:i+1}))}function V0(r,e,t,n,o,s,a=0){let i=B(r),l=T=>sr(T,n==="okhsl"?"srgb":e,o,Rs(T.toneTarget,i)),u=T=>n==="hct"&&s===se?Oe(l(T),e):l(T),c=257,m=Array.from({length:c},(T,M)=>2+96*M/(c-1)),p=Fr(r,e,t,n,m).stops.map(u).map((T,M)=>({tone:m[M],lab:R(T.resolved,"oklab").components})),f={count:c,tones:m,path:p},h=B(r),g=W0(f,h,a),{gap:d}=g,v=g.center,x=X0(a,g,v),_=Fe(f,v,d),y=Y0(r,e,t,n,_,u),w=y.map(T=>R(T.resolved,"oklab").components),O=w.slice(1).map((T,M)=>ar(w[M],T)),j=y.map(T=>B(T.resolved));return{stops:y,...x,gap:d,metric:"oklab-euclidean",requestedGap:$r,actualDistances:O,toneGaps:j.slice(1).map((T,M)=>j[M]-T),sourceTone:h,centerTone:v,centerAdjusted:Math.abs(v-h)>1e-6,compressed:d<$r-1e-6,widened:!1,toneMonotonic:j.every((T,M)=>!M||T<j[M-1]),distinct:Os(y),spacingError:Math.max(...O.map(T=>Math.abs(T-d))),reason:U0(a,x.brightnessLimited,d,v,h)}}var Z0=Object.freeze({"anchored-oklch@1":{model:"oklch",distribution:"even-lightness",anchor:"source",chroma:"source-relative"},"oklab-distance@1":{model:"oklch",distribution:"equal-distance",anchor:"source",chroma:"source-relative"},"okhsl-perceptual@1":{model:"okhsl",distribution:"cusp-shaped",anchor:"source",chroma:"source-relative"},"okhsl-peak@2":{model:"okhsl",distribution:"peak-shaped",anchor:"source",chroma:"source-cap"},"okhsl-peak@1":{model:"okhsl",distribution:"even-lightness",anchor:"cusp",chroma:"source-relative"},"hct-tone@1":{model:"hct",distribution:"tone-aligned",anchor:"schedule",chroma:"source-relative"}}),Ps={model:[["oklch","OKLCH"],["okhsl","OKHSL"],["hct","HCT"]],distribution:[["even-lightness","Even model lightness"],["tone-aligned","Shared CIELAB tone"],["equal-distance","Equal OKLab distance \xB7 experimental"],["cusp-shaped","Cusp-shaped \xB7 adjustable"],["peak-shaped","Cusp-shaped \xB7 full"]],anchor:[["source","Source at 500"],["schedule","Follow distribution"],["cusp","Hue cusp at 500"]],tone:[["model-lightness","Keep model lightness"],["preserve-tone","Hold CIELAB tone during Base adjustment"]],chroma:[["source-relative","Source-relative envelope"],["source-cap","Envelope + source chroma cap"]]};function Dt(r){let e=r&&typeof r=="object"&&!Array.isArray(r)?{tone:"model-lightness",...r}:r;if(!e||typeof e!="object"||Array.isArray(e))throw new TypeError("Invalid computation policy");let t=e;for(let n of Object.keys(t))if(!Object.hasOwn(Ps,n)&&n!=="version")throw new TypeError(`Unknown policy field: ${n}`);if(t.version!==void 0&&t.version!==1)throw new TypeError("Unsupported computation policy version");for(let[n,o]of Object.entries(Ps))if(!o.some(([s])=>s===t[n]))throw new TypeError(`Invalid ${n} policy`);if(t.model==="hct"&&(t.distribution!=="tone-aligned"||t.anchor!=="schedule"||t.chroma!=="source-relative"))throw new RangeError("HCT currently requires shared tone, distribution priority, and a source-relative envelope");if(t.distribution==="tone-aligned"&&t.anchor!=="schedule")throw new RangeError("Shared tone requires distribution priority");if(t.distribution==="equal-distance"&&t.tone==="preserve-tone")throw new RangeError("Equal-distance and tone preservation conflict");if(t.model==="oklch"&&(!["even-lightness","equal-distance","tone-aligned"].includes(t.distribution)||t.distribution!=="tone-aligned"&&t.anchor!=="source"))throw new RangeError("OKLCH currently supports source anchoring with even lightness or equal distance");if(t.model==="okhsl"&&(!["even-lightness","cusp-shaped","peak-shaped","tone-aligned"].includes(t.distribution)||t.distribution!=="tone-aligned"&&!["source","cusp"].includes(t.anchor)))throw new RangeError("OKHSL supports source/cusp anchoring and model-lightness distributions");return{version:1,model:t.model,distribution:t.distribution,anchor:t.anchor,chroma:t.chroma,tone:t.tone}}function Es(r){return Dt(r.pipeline??Z0[r.algorithm??"anchored-oklch@1"])}var K0=Object.freeze([{id:"okhsl-perceptual@1",label:"OKHSL perceptual",description:"Source-centered OKHSL lightness with adjustable vibrancy. sRGB gamut model; P3 output stays within sRGB."},{id:"hct-tone@1",label:"HCT tone-aligned",description:"Shared CIELAB tone ladder with CAM16 hue/chroma. Stop 500 may differ from the source."},{id:"okhsl-peak@2",label:"OKHSL peak",description:"Source anchored at 500; surrounding steps shaped toward the cusp, with chroma capped at the source."},{id:"okhsl-peak@1",legacy:!0,label:"OKHSL peak \xB7 legacy cusp",description:"Places the hue\u2019s sRGB cusp lightness at 500. Source saturation is retained before shaping; source lightness may change."},{id:"anchored-oklch@1",label:"Anchored OKLCH",description:"Linear OKLab lightness on each side of the source anchor."},{id:"oklab-distance@1",label:"OKLab distance \xB7 experimental",description:"Approximately equal path-length spacing per side of the anchor; final gamut fitting can change distances."}]);function Is(r){if(r===void 0)return;if(!r||typeof r!="object"||Array.isArray(r)||Object.keys(r).some(s=>!["anchor","hueRotation"].includes(s)))throw new TypeError("Invalid generation anchor branch");let e=r,t=e.hueRotation;if(t!==void 0&&(!t||typeof t!="object"||Array.isArray(t)||Object.keys(t).some(s=>!["light","dark"].includes(s))||Object.values(t).some(s=>!Number.isFinite(s)||Math.abs(s)>180)))throw new RangeError("Hue rotations must be signed degrees in [-180,180]");let n=e.anchor===void 0?{}:e.anchor;if(!n||typeof n!="object"||Array.isArray(n)||Object.keys(n).some(s=>!["L","C"].includes(s)))throw new TypeError("Invalid OKLCH anchor");let o=n;if(o.L!==void 0&&(!Number.isFinite(o.L)||o.L<0||o.L>1))throw new RangeError("Anchor L must lie in [0,1]");if(o.C!==void 0&&(!Number.isFinite(o.C)||o.C<0))throw new RangeError("Anchor C must be nonnegative")}function ks(r,e){if(!e||!Object.keys(e.anchor??{}).length)return r;let t=R(r,"oklch"),[n,o,s]=t.components;return{...t,components:[e.anchor?.L??n,e.anchor?.C??o,s]}}function J0(r,e,t,n,o,s,a){if(r!=="layered@1"&&!K0.some(i=>i.id===r))throw new TypeError(`Unsupported computation algorithm: ${r}`);if(r==="layered@1"&&!e)throw new TypeError("Layered computation requires a policy");if(!["oklch-prime@1","tone-prime@2","tone-prime@3","model-prime@1",lr,zr,ir].includes(t))throw new TypeError("Unsupported prime recipe");if(n!==void 0&&(!Number.isFinite(n)||n<0||n>100))throw new RangeError("Global vibrancy must lie in [0,100]");for(let i of o)if(!Number.isFinite(i)||i<0||i>100)throw new RangeError("Chroma factors must lie in [0,100]");if(s!==void 0&&(!Number.isInteger(s)||s<0||s>2))throw new RangeError("Prime brightness steps must be an integer from 0 to 2");if(a!==void 0&&!["off",se].includes(a))throw new TypeError("Unsupported HCT hue balance recipe")}function js(r={}){if(!r||typeof r!="object"||Array.isArray(r))throw new TypeError("Settings must be an object");let{algorithm:e="anchored-oklch@1",baseChroma:t=100,primeChroma:n=100,vibrancy:o=50,primeRecipe:s=lr,pipeline:a,base:i,prime:l,hctHueBalance:u,primeBrightnessSteps:c,globalVibrancy:m,...p}=r;J0(e,a,s,m,[t,n,o],c,u);for(let f of[i,l])Is(f);return{...m!==void 0?{globalVibrancy:m}:{},...c!==void 0?{primeBrightnessSteps:c}:{},...u!==void 0?{hctHueBalance:u}:{},...i?{base:i}:{},...l?{prime:l}:{},...Et(p),algorithm:e,baseChroma:t,primeChroma:n,vibrancy:o,primeRecipe:[zr,ir].includes(s)?s:lr,...a?{pipeline:Dt(a)}:{}}}function Q0(r={},e={}){let t=js(r);if(!e||typeof e!="object"||Array.isArray(e))throw new TypeError("Context settings must be an object");let n=e;if(Object.hasOwn(n,"globalVibrancy"))throw new TypeError("Global vibrancy cannot be overridden per palette");if(Object.hasOwn(n,"primeBrightnessSteps"))throw new TypeError("Prime brightness is global only");if(Object.hasOwn(n,"hctHueBalance"))throw new TypeError("HCT hue balance is global only");if(Object.hasOwn(n,"samplingStep"))throw new TypeError("Base sampling is global only");if(Object.hasOwn(n,"primeChroma")||Object.hasOwn(n,"primeRecipe"))throw new TypeError("Prime chroma is global only");for(let a of["base","prime"])Is(n[a]);let o={...t,...n};for(let a of["base","prime"])(t[a]||n[a])&&(o[a]={anchor:{...t[a]?.anchor,...n[a]?.anchor},hueRotation:{...t[a]?.hueRotation,...n[a]?.hueRotation}});return n.algorithm&&!n.pipeline&&delete o.pipeline,{...js(o),baseChroma:t.baseChroma*(n.baseChroma??100)/100,primeChroma:t.primeChroma}}var Gr=r=>({colorSpace:"oklch",components:r,alpha:1}),Ns=(r,e)=>`color(${r} ${e.components.map(t=>Math.max(0,Math.min(1,t))).join(" ")})`;function Bt(r,e,t){let n=me(r,e),o=R(n,e);return{stop:t,requested:r,resolved:n,target:o,mapped:n.components[1]<r.components[1]-1e-8,css:Ns(e,o)}}function eu(r,e){let t=o=>{let s=[0];for(let a=1;a<o.length;a++){let i=o[a-1].resolved.components,l=o[a].resolved.components;s.push(s.at(-1)+Math.hypot(l[0]-i[0],l[1]-i[1]))}return o.map((a,i)=>{if(i===0||i===o.length-1)return a;let l=s.at(-1)*i/(o.length-1),u=1;for(;s[u]<l;)u++;let c=(l-s[u-1])/(s[u]-s[u-1]),m=o[u-1].resolved.components,p=o[u].resolved.components,f=Bt(Gr([m[0]+(p[0]-m[0])*c,m[1]+(p[1]-m[1])*c,m[2]]),e,a.stop);return{...f,mapped:f.mapped||o[u-1].mapped||o[u].mapped}})},n=r.findIndex(o=>o.stop===500);return[...t(r.slice(0,n+1)),...t(r.slice(n)).slice(1)]}function ru(r){return r.model==="hct"?"hct-tone@1":r.model==="okhsl"?r.distribution==="peak-shaped"?"okhsl-peak@2":r.distribution==="cusp-shaped"?"okhsl-perceptual@1":"okhsl-peak@1":r.distribution==="equal-distance"?"oklab-distance@1":"anchored-oklch@1"}function tu(r,e){let{source:t,target:n,effective:o,policy:s,baseFactor:a}=e,i={...o,baseChroma:a,policy:s,algorithm:ru(s)},l=r.map(c=>{let m=Bt(Gr([c.resolved.components[0],c.resolved.components[1]*a/100,c.resolved.components[2]]),n,c.stop);return{...m,mapped:c.mapped||m.mapped}});i.algorithm==="oklab-distance@1"&&(l=eu(l,n));let u=["okhsl-perceptual@1","okhsl-peak@1","okhsl-peak@2","hct-tone@1"].includes(i.algorithm)?xs(t,n,i):null;if(u&&(l=u.stops),s.model==="oklch"&&s.chroma==="source-cap"){let c=R(t,"oklch").components[1]*a/100;l=l.map(m=>{let p=Bt(Gr([m.resolved.components[0],Math.min(c,m.resolved.components[1]),m.resolved.components[2]]),n,m.stop);return{...p,mapped:m.mapped||p.mapped}})}return l}function As(r,e,t){let{target:n,policy:o}=t,s=Se(r.resolved,e,o.model==="okhsl"?"srgb":n),a=R(s.resolved,n);return{...r,...s,target:a,mapped:r.mapped||s.mapped,toneTarget:e,css:Ns(n,a)}}function nu(r,e){let{source:t,target:n,effective:o,policy:s}=e,{lightnessMin:a,lightnessMax:i}=o;if(s.distribution==="tone-aligned")return r.map(l=>{let u=100*(i-(i-a)*(l.stop-50)/900);return s.model==="hct"?{...l,toneTarget:u}:As(l,u,e)});if(s.tone==="preserve-tone"){let l=$t(t,n,{...o,base:void 0,baseChroma:100,pipeline:{...s,tone:"model-lightness"}});return r.map((u,c)=>{let m=l.stops[c].resolved;return As(u,B(m),e)})}return r}function ou(r,e){let{target:t,effective:n,policy:o}=e;return r=r.map(s=>sr(s,o.model==="okhsl"?"srgb":t,n.base?.hueRotation,(s.stop-500)/450)),o.model==="okhsl"&&t!=="srgb"&&(r=r.map(s=>{let a=R(s.resolved,t);return{...s,target:a,css:`color(${t} ${a.components.join(" ")})`}})),o.model==="hct"&&n.hctHueBalance===se&&(r=r.map(s=>Oe(s,t))),n.globalVibrancy===0&&(r=r.map(s=>({...s,...Se(Gr([.5,0,0]),B(s.resolved),t)}))),r}function $t(r,e="srgb",t={},n={}){let o=Q0(t,n),s=ks(r,o.prime);r=ks(r,o.base);let a=Es(o),i=(o.globalVibrancy??100)/100,l=o.baseChroma*i,u=o.primeChroma*i,{lightnessMin:c,lightnessMax:m,chromaFalloff:p,samplingStep:f}=o,h=bs(r,e,{lightnessMin:c,lightnessMax:m,chromaFalloff:p,samplingStep:f}),g={source:r,target:e,effective:o,policy:a,baseFactor:l},d=tu(h.stops,g);d=nu(d,g),d=ou(d,g);let v=qr(r,d),x=Ts(s,e,u,a.model,o.prime?.hueRotation,o.hctHueBalance,o.primeBrightnessSteps,o.primeRecipe,{lightnessMin:c,lightnessMax:m}),_=x.stops;return{...h,generationAnchors:{base:r,prime:s},recipe:o.algorithm,settings:o,diagnostics:v,stops:d,prime:_,primeRecipe:o.primeRecipe,primeSpacing:Object.fromEntries(Object.entries(x).filter(([y])=>y!=="stops")),anchorAdjusted:v.anchorDelta>1e-6}}function Ls(r,e,t={},n={}){let o=Hr(r);return Object.fromEntries(Object.entries(o.colors).map(([s,a])=>[s,{...$t(a,e,t,n[s]),sourcePolicy:o.traces[s]}]))}var qs={algorithm:"hct-tone@1",baseChroma:60,primeChroma:80,lightnessMin:.05,lightnessMax:1,chromaFalloff:1.5,samplingStep:25,vibrancy:50,primeRecipe:"model-prime@2"};var Wr={kind:"color-theme",schemaVersion:2,identity:{id:"foundation-twelve",name:"Twelve foundation colors"},defaults:{target:"srgb",generation:{recipe:"hct-tone@1",lightnessMin:.05,lightnessMax:1,chromaFalloff:1.5,samplingStep:25,primeChroma:85,vibrancy:50,primeRecipe:"model-prime@4",baseChroma:50,hctHueBalance:"hct-hue-balance@1",primeBrightnessSteps:0},primaryForeground:"white@1"},palettes:{"color-1":{label:"Color 1",seed:{colorSpace:"oklch",components:[.62,.16,235],alpha:1}},"color-2":{label:"Color 2",seed:{colorSpace:"oklch",components:[.62,.16,265],alpha:1}},"color-3":{label:"Color 3",seed:{colorSpace:"oklch",components:[.62,.16,295],alpha:1}},"color-4":{label:"Color 4",seed:{colorSpace:"oklch",components:[.62,.16,325],alpha:1}},"color-5":{label:"Color 5",seed:{colorSpace:"oklch",components:[.62,.16,355],alpha:1}},"color-6":{label:"Color 6",seed:{colorSpace:"oklch",components:[.62,.16,25],alpha:1}},"color-7":{label:"Color 7",seed:{colorSpace:"oklch",components:[.62,.16,55],alpha:1}},"color-8":{label:"Color 8",seed:{colorSpace:"oklch",components:[.62,.16,85],alpha:1}},"color-9":{label:"Color 9",seed:{colorSpace:"oklch",components:[.62,.16,115],alpha:1}},"color-10":{label:"Color 10",seed:{colorSpace:"oklch",components:[.62,.16,145],alpha:1}},"color-11":{label:"Color 11",seed:{colorSpace:"oklch",components:[.62,.16,175],alpha:1}},"color-12":{label:"Color 12",seed:{colorSpace:"oklch",components:[.62,.16,205],alpha:1}},info:{seed:{colorSpace:"oklch",components:[.62,.16,255],alpha:1}},success:{seed:{colorSpace:"oklch",components:[.62,.16,155],alpha:1}},warning:{seed:{colorSpace:"oklch",components:[.62,.16,75],alpha:1}},danger:{seed:{colorSpace:"oklch",components:[.62,.16,25],alpha:1}},material:{seed:{colorSpace:"oklch",components:[.6,.08,235],alpha:1},label:"Neutral",sourcePolicy:{kind:"hue-from",family:"color-1",achromatic:"authored-hue"}}},core:{order:["color-1","color-2","color-3","color-4","color-5","color-6","color-7","color-8","color-9","color-10","color-11","color-12"]},bindings:{brand:{primary:"color-1",secondary:"color-11",tertiary:"color-3"},material:"material",feedback:{info:"info",success:"success",warning:"warning",danger:"danger"},adapters:{},data:{categorical:{default:{recipe:"categorical-samples@1",palettes:["color-1","color-2","color-3","color-4","color-5","color-6","color-7","color-8","color-9","color-10","color-11","color-12"],sample:{output:"prime",sample:"prime"}}}},families:{blue:"color-1",indigo:"color-2",purple:"color-3",pink:"color-4",red:"color-5",orange:"color-6",amber:"color-7",yellow:"color-8",lime:"color-9",green:"color-10",teal:"color-11",cyan:"color-12"}},libraries:[],scrims:{recipe:"scrim-recipes@1",alphaStep:.025,anchors:{}}};var Hs="hct-palettes@4",iu=r=>(r%360+360)%360,Re=(r,e,t,n)=>{if(typeof r!="number"||!Number.isFinite(r)||r<t||r>n)throw new RangeError(`${e} must be a finite number in [${t},${n}]`);return r},lu=new Set(["preset","hue","hues","count","chroma","tone","balance","output","system","material","target","base","prime","toneMin","toneMax","step","falloff","source","hueBalance","primeBrightnessSteps","primeSpacing"]);function cu(r){if(!r||typeof r!="object"||Array.isArray(r))throw new TypeError("Request must be an object");for(let n of Object.keys(r))if(!lu.has(n))throw new TypeError(`Unknown request field: ${n}`);let e=r.preset==="project";if(r.preset!==void 0&&!e)throw new TypeError("Only preset project is supported");if(e&&["hue","hues","count","chroma","tone","balance","source"].some(n=>Object.hasOwn(r,n)))throw new TypeError("Project preset retains exact authored seeds; omit hue/count/chroma/tone/balance/source");if(Object.hasOwn(r,"source")&&(!r.source||typeof r.source!="object"||Array.isArray(r.source)))throw new TypeError("source must be a tagged color object");if(Object.hasOwn(r,"hues")&&!Array.isArray(r.hues))throw new TypeError("hues must be an array");if(r.source&&["hue","hues","chroma","tone"].some(n=>Object.hasOwn(r,n)))throw new TypeError("Tagged source cannot be combined with HCT seed coordinates");let t=r.count??r.hues?.length??(e?12:1);if(![1,2,3,4,6,8,12].includes(t))throw new RangeError("Count must be 1, 2, 3, 4, 6, 8, or 12");if(r.source&&t!==1)throw new TypeError("Tagged source supports a single core palette");if(r.hues&&Object.hasOwn(r,"hue"))throw new TypeError("Use hue or hues, not both");return{isProject:e,count:t}}function uu(r,e){let t=r.hues??Array.from({length:e},(o,s)=>(r.hue??230)+360*s/e);if(!Array.isArray(t)||t.length!==e)throw new TypeError("hues must match count");t=t.map(o=>iu(Re(o,"hue",-36e3,36e3)));let n=t;if(new Set(n).size!==n.length)throw new TypeError("Core hues must be distinct");return n}function mu(r,e,t,n,o,s){let{baseChroma:a,primeChroma:i}=s?Wr.defaults.generation:{baseChroma:60,primeChroma:80};return{...qs,primeRecipe:{balanced:"model-prime@4",tone:"model-prime@3",distance:"model-prime@2"}[t],hctHueBalance:n?se:"off",primeBrightnessSteps:o,baseChroma:Re(r.base??(e?100:a),"base",0,100),primeChroma:Re(r.prime??(e?100:i),"prime",0,100),lightnessMin:Re(r.toneMin??5,"toneMin",0,100)/100,lightnessMax:Re(r.toneMax??100,"toneMax",0,100)/100,samplingStep:r.step??25,chromaFalloff:r.falloff??1.5}}function pu(r={}){let{isProject:e,count:t}=cu(r),n=uu(r,t),o=r.chroma??48;o!=="max"&&Re(o,"chroma",0,200);let s=Re(r.tone??60,"tone",2,98),a=r.target??"srgb";if(!["srgb","display-p3"].includes(a))throw new TypeError("Target must be srgb or display-p3");let i=r.output??(e?"base-primes":"base");if(!["base","primes","base-primes"].includes(i))throw new TypeError("Output must be base, primes, or base-primes");let l=r.balance??t>1;if(typeof l!="boolean")throw new TypeError("balance must be boolean");let u=r.system??e;if(typeof u!="boolean")throw new TypeError("system must be boolean");let c=r.material??(e?"tinted":"none");if(!["none","tinted","neutral"].includes(c))throw new TypeError("Material must be none, tinted, or neutral");if(r.source&&l)throw new TypeError("Do not balance an exact tagged source");let m=o==="max",p=r.hueBalance??!m;if(typeof p!="boolean")throw new TypeError("hueBalance must be boolean");let f=r.primeBrightnessSteps??0;if(!Number.isInteger(f)||f<0||f>2)throw new RangeError("primeBrightnessSteps must be an integer from 0 to 2");let h=r.primeSpacing??(m?"tone":"balanced");if(!["balanced","tone","distance"].includes(h))throw new TypeError("primeSpacing must be balanced, tone or distance");let g=mu(r,m,h,p,f,e);return{version:Hs,preset:e?"project":"hct",count:t,hues:n,chroma:o,tone:s,balance:l,output:i,system:u,material:c,target:a,settings:g,...r.source?{source:structuredClone(r.source)}:{}}}var du=Wr.palettes,zt=r=>structuredClone(du[r].seed);function Fs(r,e,t){if(e===0||e===100)return 0;for(let n=64;n<=1024;n*=2){let o=te(r,n,e,t);if(o.mapped)return oe(o.resolved)[1]}throw new RangeError("Could not bracket HCT gamut boundary below chroma 1024")}function fu(r){let{preset:e,count:t,hues:n,chroma:o,tone:s,balance:a,target:i}=r,l={},u={},c={},m;if(e==="project"){m=[...Wr.core.order];for(let p of m)l[p]=zt(p)}else if(m=Array.from({length:t},(p,f)=>`color-${f+1}`),r.source)l[m[0]]=structuredClone(r.source);else{let p=n.map(h=>Fs(h,s,i)),f=Math.min(o==="max"?1/0:o,...p);for(let h=0;h<t;h++){let g=a?f:Math.min(o==="max"?1/0:o,p[h]);l[m[h]]=te(n[h],g,s,i).resolved,c[m[h]]={colorSpace:"hct",components:[n[h],o,s],fittedHct:oe(l[m[h]]),capacity:p[h],balancedChroma:a?f:null}}}if(r.system)for(let p of["info","success","warning","danger"])l[p]=zt(p);if(r.material!=="none"){let p=zt("material");l.material=p,r.material==="neutral"?p.components[1]=0:u.material={kind:"hue-from",family:m[0],achromatic:"authored-hue"}}return{colors:l,rules:u,seedIntent:c,core:m}}function hu(r,e,t,n,o,s){let{hues:a,chroma:i,target:l,settings:u}=r,c=a[e],m=Math.abs(o-500)/450,p=i==="max"?t*u.baseChroma/100:Math.min(t,n*(1-m**u.chromaFalloff)*u.baseChroma/100),f=te(c,p,s,l),h=R(f.resolved,l);return{stop:o,toneTarget:s,requested:{colorSpace:"hct",components:[c,p,s],alpha:1},resolved:f.resolved,target:h,mapped:f.mapped,modelCoordinates:[c,p,s],css:`color(${l} ${h.components.map(g=>Math.max(0,Math.min(1,g))).join(" ")})`}}function bu(r,e,t,n){let{hues:o,chroma:s,balance:a,target:i,settings:l}=r,u=e[n[0]].stops.map(m=>({stop:m.stop,t:m.toneTarget})),c=u.map(({t:m})=>o.map(p=>Fs(p,m,i)));for(let m=0;m<n.length;m++){let p=e[n[m]];p.stops=u.map(({stop:f,t:h},g)=>{let d=a?Math.min(...c[g]):c[g][m],v=oe(t[n[m]])[1];return{...hu(r,m,d,v,f,h),gamutBoundary:c[g][m]}}),l.hctHueBalance===se&&(p.stops=p.stops.map(f=>Oe(f,i))),p.recipe=s==="max"?"hct-gamut-boundary@1":"hct-balanced-envelope@1",p.diagnostics=qr(t[n[m]],p.stops),p.anchorAdjusted=p.diagnostics.anchorDelta>1e-6,p.settings={...p.settings,algorithm:p.recipe}}}function gu(r,e){return Object.fromEntries(Object.entries(r).map(([t,n])=>{let o={...n};return e==="base"&&delete o.prime,e==="primes"&&delete o.stops,[t,o]}))}function vu(r,e,t,n){return["Base labels are positions, not HCT tones. 050 is light and 950 is dark.",`Seven Primes use ${r.primeRecipe}; tone-aligned HCT shares the Base envelope, while legacy distance spacing remains selectable.`,...r.hctHueBalance===se?["HCT hue balance gently warms yellow shadows at fixed tone. Final hues and chromas can differ from the balanced or maximum envelope before this adjustment."]:[],...e&&t!=="project"?["Core balance aligns tones and caps Base CAM16 chroma to shared feasible capacity; angular hue spacing and chroma equality do not certify visual equality."]:[],...n==="max"?["Max mode replaces core Base envelopes with per-tone gamut boundaries; balanced sets use the smallest core capacity at each tone. Prime remains the independent project scheduler, not a per-sample maximum."]:[],"System seeds and tinted Material preserve project OKLCH defaults; HCT angles are never reused as OKLCH angles.","This is generated source-palette data, not a semantic theme, importable session, accessibility assessment or Material Design native algorithm parity claim."]}function Ds(r={}){let e=pu(r),{preset:t,chroma:n,balance:o,target:s,settings:a}=e,{colors:i,rules:l,seedIntent:u,core:c}=fu(e),m={schemaVersion:2,colors:i,sourcePolicies:{version:"source-policies@1",rules:l}},p=Ls(m,s,a),f=Hr(m).colors;(n==="max"||o)&&t!=="project"&&bu(e,p,f,c);let h=gu(p,e.output);return{kind:"hct-palette-output",version:1,generator:Hs,request:e,core:c,order:Object.keys(i),sources:m,seedIntent:u,palettes:h,notes:vu(a,o,t,n)}}function yu(r){let e=[":root {"],t=[];for(let[o,s]of Object.entries(r.palettes)){let a=[["Base",s.stops],["Prime",s.prime]].filter(([,l])=>l),i=[];for(let[l,u]of a){let c=[];for(let m of u){let p=l==="Base"?String(m.stop).padStart(3,"0"):String(m.name??m.key??m.stop),f=`${o}-${l.toLowerCase()}-${p}`;e.push(`  --${f}: ${m.css};`),c.push(`<div class="sample"><div class="paint" style="background:var(--${f})"></div><strong>${p}</strong><code>${m.css}</code></div>`)}i.push(`<h3>${l}</h3><div class="samples">${c.join("")}</div>`)}t.push(`<section><h2>${o}</h2>${i.join("")}</section>`)}e.push("}");let n=`<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HCT palettes</title><link rel="stylesheet" href="palettes.css"><style>body{font:16px/1.5 system-ui;margin:2rem;background:#181a1e;color:#eee}section{margin-block:2rem}.samples{display:grid;grid-template-columns:repeat(auto-fit,minmax(110px,1fr));gap:12px}.paint{height:72px;border-radius:12px}code{font:11px/1.4 monospace;display:block;overflow-wrap:anywhere;color:#bbb}h2,h3{margin-bottom:12px}</style><h1>HCT palettes</h1><p>${r.order.length} source palettes \xB7 ${r.request.target} \xB7 ${r.request.output}</p><p>Full precision and recipe diagnostics: palettes.json. This preview does not evaluate accessibility or certify visual balance.</p>${t.join("")}</html>`;return{css:e,html:n}}async function _u(){let r=process.argv.slice(2);if(r.length===1&&r[0]==="--help")console.log(`Usage: node generate.cjs --request request.json --out NEW_DIRECTORY
Writes palettes.json, sources.json, palettes.css and preview.html. Node 22+; no npm or network needed.`);else try{if(r.length!==4||r[0]!=="--request"||r[2]!=="--out")throw new Error("Use --request request.json --out NEW_DIRECTORY");let e=Ds(JSON.parse(await Ur.default.readFile(r[1],"utf8"))),t=Gt.default.resolve(r[3]),{css:n,html:o}=yu(e);await Ur.default.mkdir(t),await Promise.all([["palettes.json",JSON.stringify(e,null,2)+`
`],["sources.json",JSON.stringify(e.sources,null,2)+`
`],["palettes.css",n.join(`
`)+`
`],["preview.html",o]].map(([s,a])=>Ur.default.writeFile(Gt.default.join(t,s),a,{flag:"wx"}))),console.log(JSON.stringify({directory:t,palettes:e.order.length,output:e.request.output,files:["palettes.json","sources.json","palettes.css","preview.html"]}))}catch(e){console.error(e.message),process.exitCode=1}}_u().catch(r=>{console.error(r.message),process.exitCode=1});
