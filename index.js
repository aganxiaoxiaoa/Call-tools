#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const axios = require('axios');
const cheerio = require('cheerio');
const chalk = require('chalk');
const cron = require('node-cron');
const { XMLParser } = require('fast-xml-parser');
const yargs = require('yargs/yargs');
const { hideBin } = require('yargs/helpers');

const BANNED_PHRASES = [
  "in today's competitive market", "this comprehensive guide", "unlock the secrets", "game-changing",
  "revolutionary", "seamless experience", "elevate your business", "at the end of the day",
  "in conclusion", "whether you are a startup or an established business"
];

const INDUSTRY_TERMS = {
  apparel: {
    industry: ['GSM', 'MOQ', 'tech pack', 'cut-and-sew', 'private label', 'lead time', 'QA/QC'],
    buyer: ['bulk order', 'custom logo', 'fabric sourcing', 'sample approval', 'production timeline'],
    technical: ['Pantone matching', 'stitch density', 'pre-shrunk cotton', 'AQL inspection', 'size grading']
  },
  'essential-oil': {
    industry: ['GC/MS', 'COA', 'MSDS', 'IFRA', 'steam distillation', 'cold-pressed'],
    buyer: ['white label oils', 'therapeutic grade', 'private blend', 'batch consistency', 'supply stability'],
    technical: ['linalool', 'terpene profile', 'oxidation stability', 'amber glass', 'allergen disclosure']
  }
};

function out(txt) { console.log(process.stdout.isTTY ? chalk.cyan(txt) : txt); }
function readText(file) { return fs.readFileSync(path.resolve(file), 'utf8'); }
function safeRead(file) { return fs.existsSync(file) ? fs.readFileSync(file, 'utf8') : ''; }
function words(t){return (t.toLowerCase().match(/\b[a-z0-9'-]+\b/g)||[]);}
function splitSentences(t){return t.split(/(?<=[.!?])\s+/).filter(Boolean);}

function parseSitemapXml(xml) {
  const parser = new XMLParser({ ignoreAttributes: false });
  const obj = parser.parse(xml);
  const urls = obj.urlset?.url || [];
  return (Array.isArray(urls) ? urls : [urls]).map(u => ({
    url: u.loc,
    date: u.lastmod || '',
    image: u['image:image']?.['image:loc'] || '',
    title: decodeURIComponent((u.loc || '').split('/').pop() || '').replace(/[-_]/g, ' ')
  }));
}

function mdHeadings(text, prefix) { return text.split('\n').filter(l => l.startsWith(prefix)); }
function firstMarkdownTitle(text){return text.split('\n').find(l=>l.startsWith('# '))?.replace('# ','').trim()||'';}
function metaDescription(text){return text.match(/meta\s*description\s*:\s*(.+)/i)?.[1]?.trim()||'';}

const argv = yargs(hideBin(process.argv))
.command('blog-sync', 'Sync Shopify blog sitemap against local category index', y=>y.option('url',{type:'string',demandOption:true}).option('category',{type:'string',demandOption:true}), async a=>{
  try {
    const mapUrl = `${a.url.replace(/\/$/,'')}/sitemap_blogs_1.xml`;
    const xml = (await axios.get(mapUrl, { timeout: 20000 })).data;
    const remote = parseSitemapXml(xml);
    const indexPath = `D:/唐广/veytis.com/参考/${a.category}_blog_index.md`;
    const local = safeRead(indexPath);
    const localUrls = new Set((local.match(/https?:\/\/\S+/g)||[]));
    const remoteUrls = new Set(remote.map(r=>r.url));
    const added = remote.filter(r=>!localUrls.has(r.url));
    const removed = [...localUrls].filter(u=>!remoteUrls.has(u));
    out(`blog-sync report for ${a.category}`);
    out(`New: ${added.length}`); added.forEach(i=>out(` + ${i.title} | ${i.url}`));
    out(`Removed: ${removed.length}`); removed.forEach(u=>out(` - ${u}`));
    out(`Changed: 0 (date/image diff not tracked from markdown index)`);
  } catch (e) { console.error(`Error: blog-sync failed - ${e.message}`); process.exitCode=1; }
})
.command('site-health', 'Check sitemap URLs for broken pages', y=>y.option('url',{type:'string',demandOption:true}), async a=>{
  try{
    const xml = (await axios.get(a.url)).data;
    const urls = parseSitemapXml(xml).map(x=>x.url);
    const broken=[];
    for (const u of urls){
      try { const r=await axios.get(u,{validateStatus:()=>true,timeout:12000}); if(r.status>=400) broken.push([u,r.status]); }
      catch { broken.push([u,'ERR']); }
    }
    out(`Checked ${urls.length} pages`);
    if(!broken.length) out('No broken links found.');
    else broken.forEach(([u,s])=>out(`BROKEN ${s} ${u}`));
  } catch(e){ console.error(`Error: site-health failed - ${e.message}`); process.exitCode=1; }
})
.command('seo-check','SEO checks for markdown', y=>y.option('file',{type:'string',demandOption:true}), a=>{
  const t=readText(a.file); const h2=mdHeadings(t,'## ').length; const title=firstMarkdownTitle(t); const meta=metaDescription(t); const low=t.toLowerCase();
  const banned=BANNED_PHRASES.filter(p=>low.includes(p)); const ws=words(t); const keyword=words(title).slice(0,2).join(' ');
  const density = keyword ? ((low.split(keyword).length-1)/Math.max(ws.length,1)*100).toFixed(2) : '0.00';
  const rows=[
    ['H2 count (6-7)',h2, h2>=6&&h2<=7],['Title length (50-60)',title.length,title.length>=50&&title.length<=60],
    ['Meta desc length (150-160)',meta.length,meta.length>=150&&meta.length<=160],['Banned phrases',banned.length,banned.length===0],
    ['Keyword density %',density,Number(density)>=0.8&&Number(density)<=2.5]
  ];
  rows.forEach(r=>out(`${r[0]} | ${r[1]} | ${r[2]?'PASS':'FAIL'}`)); if(banned.length) out(`Banned hits: ${banned.join('; ')}`);
})
.command('keyword-extract','Generate long-tail B2B keywords', y=>y.option('topic',{type:'string',demandOption:true}), a=>{
  const t=a.topic.toLowerCase();
  const ks=[`what is ${t} for wholesale buyers`,`${t} supplier selection checklist`,`${t} MOQ and lead time comparison`,`best ${t} private label manufacturer`,`${t} quality control standards`,`${t} pricing factors for importers`,`${t} OEM vs ODM decision guide`];
  ['awareness','consideration','decision'].forEach((s,i)=>out(`${s}: ${ks.slice(i*2,i*2+2).join(' | ')}`));
})
.command('geo-audit','Audit GEO readability', y=>y.option('file',{type:'string',demandOption:true}), a=>{const t=readText(a.file); const ps=t.split(/\n\n+/); let score=0;
  const direct=/^##\s*(answer|summary|key takeaways)/im.test(t); if(direct) score+=2; const faq=/\?\n/i.test(t); if(faq) score+=2;
  const entities=(t.match(/\b[A-Z][a-z]+\b/g)||[]).length; if(entities>10) score+=2; const heads=mdHeadings(t,'## ').length; if(heads>=4) score+=2;
  const concise=ps.filter(p=>words(p).length<=90).length/Math.max(ps.length,1); if(concise>0.6) score+=2; out(`GEO score: ${score}/10`);
})
.command('faq-gen','Generate FAQ JSON', y=>y.option('file',{type:'string',demandOption:true}), a=>{const t=readText(a.file); const h2=mdHeadings(t,'## ').map(s=>s.replace('## ','').trim()).slice(0,5);
  const faqs=h2.map(h=>({question:`What should buyers know about ${h.toLowerCase()}?`,answer:`Buyers should confirm requirements, timelines, compliance, and supplier capabilities for ${h.toLowerCase()}.`}));
  console.log(JSON.stringify(faqs,null,2));
})
.command('blog-plan','Plan unique blog angle', y=>y.option('topic',{type:'string',demandOption:true}).option('category',{type:'string',demandOption:true}), a=>{const idx=safeRead(`D:/唐广/veytis.com/参考/${a.category}_blog_index.md`).toLowerCase();
  const topicWords=words(a.topic); const overlap=topicWords.filter(w=>idx.includes(w)).length; const score=overlap===0?'none':overlap<=2?'low':overlap<=4?'medium':'high';
  out(`Overlap score: ${score}`); out(`Matched blog numbers: unknown (index format dependent)`); out(`Suggested unique angle: Focus on procurement risks and supplier verification for ${a.topic}.`);
  out(`Recommended keywords: ${a.topic} supplier, ${a.topic} MOQ, ${a.topic} lead time`); out('Buyer stage: consideration'); out('Topics to avoid: generic definitions already covered.');
})
.command('content-gap','Find uncovered topics', y=>y.option('category',{type:'string',demandOption:true}), a=>{const idx=safeRead(`D:/唐广/veytis.com/参考/${a.category}_blog_index.md`).toLowerCase();
  const candidates=['MOQ negotiation tactics','quality inspection checklist','supplier onboarding SOP','incoterms risk control','sample approval workflow'];
  const rank=candidates.filter(c=>!idx.includes(c.split(' ')[0].toLowerCase())); rank.forEach((r,i)=>out(`${i+1}. ${r}`));
})
.command('prose-check','Editorial prose checks', y=>y.option('file',{type:'string',demandOption:true}), a=>{const t=readText(a.file); const ss=splitSentences(t); const weak=(t.match(/\b(very|really|quite|actually)\b/gi)||[]).length;
  const long=ss.filter(s=>words(s).length>30).length; const passive=(t.match(/\b(is|are|was|were|been|be)\s+\w+ed\b/gi)||[]).length;
  const starts={}; ss.forEach(s=>{const w=words(s)[0]||''; starts[w]=(starts[w]||0)+1}); const repeated=Object.entries(starts).filter(([,c])=>c>2).map(([w])=>w);
  const readability=Math.max(0,100-long*2-passive-weak);
  out(`Passive voice hits: ${passive}`); out(`Weak adverbs: ${weak}`); out(`Long sentences: ${long}`); out(`Readability score: ${readability}/100`); out(`Repeated starts: ${repeated.join(', ')||'none'}`);
})
.command('banned-phrases','Find banned phrases', y=>y.option('file',{type:'string',demandOption:true}), a=>{const t=readText(a.file); const low=t.toLowerCase();
  BANNED_PHRASES.forEach(p=>{const i=low.indexOf(p); if(i>=0) out(`${p} => ...${t.slice(Math.max(0,i-30), i+p.length+30).replace(/\n/g,' ')}...`);});
})
.command('diff-check','Find content overlap', y=>y.option('file',{type:'string',demandOption:true}).option('category',{type:'string'}).option('compare',{type:'string'}), a=>{const t1=readText(a.file); const base=a.compare?readText(a.compare):safeRead(`D:/唐广/veytis.com/参考/${a.category}_blog_index.md`);
  const p1=t1.split(/\n\n+/).map(s=>s.trim()).filter(s=>s.length>40); const reps=p1.filter(p=>base.includes(p.slice(0,80)));
  const h1=mdHeadings(t1,'## ').length; const h2=mdHeadings(base,'## ').length; const keys=words(t1).filter((w,i,arr)=>arr.indexOf(w)===i&&w.length>6).slice(0,20).filter(w=>base.includes(w));
  out(`Repeated paragraphs: ${reps.length}`); out(`Similar heading structures: ${Math.min(h1,h2)}/${Math.max(h1,h2)||1}`); out(`Overlapping keywords: ${keys.slice(0,10).join(', ')}`);
})
.command('industry-terms','Output industry lexicon', y=>y.option('category',{type:'string',choices:['apparel','essential-oil'],demandOption:true}), a=>{const d=INDUSTRY_TERMS[a.category];
  out(`Industry terms: ${d.industry.join(', ')}`); out(`Buyer phrases: ${d.buyer.join(', ')}`); out(`Technical vocabulary: ${d.technical.join(', ')}`);
})
.command('cro-audit','Conversion audit', y=>y.option('file',{type:'string',demandOption:true}), a=>{const t=readText(a.file).toLowerCase(); let score=0;
  const cta=/(contact us|get quote|request sample|book call)/.test(t); if(cta) score+=2; const pain=/(challenge|pain point|problem|risk)/.test(t); if(pain) score+=2;
  const proof=/(case study|testimonial|client|certified)/.test(t); if(proof) score+=2; const objection=/(faq|objection|concern|guarantee)/.test(t); if(objection) score+=2;
  const next=/(next step|email|whatsapp|form)/.test(t); if(next) score+=2; out(`CRO score: ${score}/10`);
})
.command('image-prompt','Generate image prompts', y=>y.option('section',{type:'string',demandOption:true}).option('style',{type:'string',default:'B2B commercial'}), a=>{
  out(`Midjourney: ${a.section}, ${a.style}, commercial photography, softbox lighting, realistic texture, 8k --ar 16:9 --v 6`);
  out(`DALL-E: Create a ${a.style} scene of ${a.section}; realistic corporate editorial photo, high detail, natural color grading.`);
  out(`Stable Diffusion: ${a.section}, ${a.style}, professional product photography, ultra-detailed, sharp focus, 35mm lens, studio lighting.`);
})
.command('image-fetch','Download HD images from Pexels', y=>y.option('section',{type:'string',demandOption:true}).option('query',{type:'string',demandOption:true}).option('category',{type:'string',demandOption:true}), async a=>{
  try{const key=process.env.PEXELS_API_KEY; if(!key) throw new Error('PEXELS_API_KEY is missing');
    const dir=path.resolve(`D:/bot/tool/blog_images/${a.category}/${a.section}`); fs.mkdirSync(dir,{recursive:true});
    const r=await axios.get('https://api.pexels.com/v1/search',{params:{query:a.query,per_page:2},headers:{Authorization:key}});
    let saved=0; for (const p of r.data.photos||[]){ const url=p.src.original||p.src.large2x; const res=await axios.get(url,{responseType:'arraybuffer'}); if(res.data.byteLength<200*1024) continue;
      const fp=path.join(dir,`${a.section}_${p.id}.jpg`); fs.writeFileSync(fp,res.data); out(`Saved ${fp}`); saved++; }
    out(`Downloaded ${saved} images.`);
  } catch(e){ console.error(`Error: image-fetch failed - ${e.message}`); process.exitCode=1; }
})
.command('cron-setup','Generate cron payload', y=>y.option('task',{type:'string',demandOption:true}).option('schedule',{type:'string',choices:['daily','weekly','monthly'],demandOption:true}).option('param',{type:'string'}), a=>{
  const map={daily:'0 9 * * *',weekly:'0 9 * * 1',monthly:'0 9 1 * *'}; const payload={task:a.task,cron:map[a.schedule],params:a.param?Object.fromEntries([a.param.split('=')]):{},valid:cron.validate(map[a.schedule])};
  console.log(JSON.stringify(payload,null,2));
})
.command('task-status','Summarize OpenClaw task logs', y=>y.option('task-id',{type:'string',demandOption:true}), a=>{const log=`D:/bot/tool/openclaw/logs/${a['task-id']}.log`; if(!fs.existsSync(log)){console.error(`Error: log not found for task ${a['task-id']}`);process.exitCode=1;return;}
  const lines=fs.readFileSync(log,'utf8').trim().split('\n'); out(`Task ${a['task-id']} last status:`); out(lines.slice(-5).join('\n'));})
.command('fact-check','Flag unverifiable claims', y=>y.option('file',{type:'string',demandOption:true}), a=>{const t=readText(a.file); const ss=splitSentences(t);
  const rx=/(\d+%|\$\d+|MOQ|minimum order|capacity|certif|ISO|FDA|delivery|days|lead time|legal|medical|cure|treat)/i;
  const hits=ss.filter(s=>rx.test(s)); if(!hits.length) out('No obvious unverifiable claims detected.');
  hits.forEach((s,i)=>out(`${i+1}. UNVERIFIED: ${s.trim()} [Source confirmation required]`));
})
.demandCommand(1)
.help().argv;
