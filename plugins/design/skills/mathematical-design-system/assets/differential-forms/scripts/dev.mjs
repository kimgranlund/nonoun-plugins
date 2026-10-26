import './build.mjs';
import {createServer} from 'node:http';
import {readFileSync} from 'node:fs';
const port=Number(process.env.PORT??4173);
createServer((req,res)=>{
 if(req.url!=='/'&&req.url!=='/index.html'){res.writeHead(404);res.end('Not found');return;}
 res.writeHead(200,{'Content-Type':'text/html; charset=utf-8','Cache-Control':'no-store'});
 res.end(readFileSync(new URL('../specimens/index.html',import.meta.url)));
}).listen(port,'127.0.0.1',()=>console.log(`Differential Forms: http://localhost:${port}`));
