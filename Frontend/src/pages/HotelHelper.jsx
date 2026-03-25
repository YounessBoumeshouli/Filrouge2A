import React, { useState, useEffect, useRef } from 'react';

/* ══════════════════════════════════════════════════════════════════
   FONTS
   ══════════════════════════════════════════════════════════════════ */
const FontLink = () => {
  useEffect(() => {
    const l = document.createElement('link');
    l.rel  = 'stylesheet';
    l.href = 'https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;1,300;1,400&family=Jost:wght@300;400;500;600&display=swap';
    document.head.appendChild(l);
  }, []);
  return null;
};

/* ══════════════════════════════════════════════════════════════════
   DESIGN TOKENS — identical to SoukPrice / PriceDetection
   ══════════════════════════════════════════════════════════════════ */
const C = {
  cream : '#F5F0E8',
  warm  : '#FAF7F2',
  panel : '#EDEAE3',
  dark  : '#1C1A17',
  mid   : '#5C5549',
  soft  : '#9d9080',
  terra : '#B5451B',
  terraL: '#D4603A',
  gold  : '#C4962A',
  border: 'rgba(28,26,23,0.09)',
  serif : "'Cormorant Garamond', Georgia, serif",
  sans  : "'Jost', sans-serif",
};

/* ══════════════════════════════════════════════════════════════════
   HOTEL DATABASE — 18 real Marrakech hotels
   ══════════════════════════════════════════════════════════════════ */
const HOTELS = [
  {
    id:1, name:'La Mamounia', arabic:'لا ماموينا',
    stars:5, pricePerNight:4200, beds:2, area:'Hivernage',
    distanceMedina:1.2, distanceSouk:1.8,
    tags:['Legendary','Pool','Spa','Fine Dining','Gardens'],
    type:'Palace Hotel',
    amenities:['🏊 Pool','💆 Spa','🍽️ 5 Restaurants','🌿 Gardens','🏋️ Gym','🚗 Valet'],
    description:'The legendary palace hotel of Marrakech, frequented by royalty and stars. Set within 17 acres of gardens with Churchill\'s favourite suite still intact.',
    rating:9.4, reviews:2841,
    gradient:'linear-gradient(135deg,#c4a050,#8b6820,#5c4210)',
    highlight:'Iconic since 1923',
  },
  {
    id:2, name:'Royal Mansour', arabic:'رويال مانسور',
    stars:5, pricePerNight:8500, beds:1, area:'Medina',
    distanceMedina:0.1, distanceSouk:0.4,
    tags:['Ultra-Luxury','Private Riads','Butler','Michelin Star'],
    type:'Palace Hotel',
    amenities:['🏊 Hammam','💆 Spa','🍽️ Michelin Restaurant','🛎️ Butler','🌿 Courtyard'],
    description:'Built by King Mohammed VI, each guest stays in their own private riad with plunge pool. The most exclusive address in all of Morocco.',
    rating:9.8, reviews:1240,
    gradient:'linear-gradient(135deg,#8c7355,#5c4a30,#3d2e1a)',
    highlight:'Private riad per guest',
  },
  {
    id:3, name:'Amanjena', arabic:'أمانجينا',
    stars:5, pricePerNight:6800, beds:1, area:'Palmeraie',
    distanceMedina:5.8, distanceSouk:6.4,
    tags:['Ultra-Luxury','Desert Views','Pool','Zen'],
    type:'Resort',
    amenities:['🏊 Pool','💆 Spa','🍽️ Restaurant','🌴 Palm Gardens','🚗 Airport Transfer'],
    description:'Set amid olive and citrus groves near the Palmeraie, this Aman resort recreates a Moorish village with private pavilions and reflecting pools.',
    rating:9.6, reviews:892,
    gradient:'linear-gradient(135deg,#6b5a3a,#4a3c24,#2d2510)',
    highlight:'Moorish pavilions',
  },
  {
    id:4, name:'Riad Kniza', arabic:'رياض كنيزة',
    stars:5, pricePerNight:1850, beds:1, area:'Medina',
    distanceMedina:0.05, distanceSouk:0.2,
    tags:['Authentic Riad','Antiques','Rooftop','Boutique'],
    type:'Boutique Riad',
    amenities:['🏊 Plunge Pool','🍽️ Riad Cuisine','☕ Rooftop Terrace','🎭 Hammam'],
    description:'An 18th-century merchant\'s home filled with museum-quality antiques, carved cedarwood and zellij tilework. Only 11 rooms — deeply personal.',
    rating:9.5, reviews:756,
    gradient:'linear-gradient(135deg,#b5451b,#7a2d10,#4a1808)',
    highlight:'18th-century antiques',
  },
  {
    id:5, name:'Selman Marrakech', arabic:'سلمان مراكش',
    stars:5, pricePerNight:3100, beds:2, area:'Hivernage',
    distanceMedina:2.1, distanceSouk:2.7,
    tags:['Arabesque','Arabian Horses','Pool','Architecture'],
    type:'Luxury Hotel',
    amenities:['🏊 Infinity Pool','🐎 Equestrian Centre','💆 Spa','🍽️ Restaurant','🏋️ Gym'],
    description:'A stunning neo-Moorish palace with an iconic infinity pool and working equestrian stables. Jacques Garcia-designed interiors of jaw-dropping grandeur.',
    rating:9.2, reviews:1580,
    gradient:'linear-gradient(135deg,#7a8c9c,#4a6070,#2d3e4a)',
    highlight:'Infinity pool + horses',
  },
  {
    id:6, name:'Dar Rhizlane', arabic:'دار ريزلان',
    stars:5, pricePerNight:1600, beds:1, area:'Palmeraie',
    distanceMedina:4.5, distanceSouk:5.1,
    tags:['Palmeraie','Gardens','Pool','Romantic'],
    type:'Boutique Riad',
    amenities:['🏊 Pool','🌿 Gardens','🍽️ Restaurant','💆 Spa','🎭 Hammam'],
    description:'A secluded haven in the Palmeraie with lush gardens, two pools, and only 15 suites. The perfect romantic retreat away from the city bustle.',
    rating:9.1, reviews:640,
    gradient:'linear-gradient(135deg,#6b9c6b,#4a7048,#2d4a2a)',
    highlight:'Lush garden retreat',
  },
  {
    id:7, name:'Riad Yasmine', arabic:'رياض ياسمين',
    stars:4, pricePerNight:620, beds:1, area:'Medina',
    distanceMedina:0.08, distanceSouk:0.15,
    tags:['Instagram Famous','Pool','Value','Central'],
    type:'Boutique Riad',
    amenities:['🏊 Pool','☕ Rooftop','🍳 Breakfast Included','📶 Fast WiFi'],
    description:'Famous for its tiled pool and photogenic blue walls, this intimate riad sits deep in the medina. A favourite of travel photographers worldwide.',
    rating:8.8, reviews:2104,
    gradient:'linear-gradient(135deg,#4a7a9c,#2d5470,#1a3448)',
    highlight:'Iconic tiled pool',
  },
  {
    id:8, name:'Les Jardins de la Medina', arabic:'حدائق المدينة',
    stars:4, pricePerNight:890, beds:2, area:'Kasbah',
    distanceMedina:0.3, distanceSouk:0.7,
    tags:['Gardens','Pool','Family','Kasbah'],
    type:'Boutique Hotel',
    amenities:['🏊 Pool','🌿 Gardens','🍽️ Restaurant','🏋️ Gym','📶 WiFi'],
    description:'A former palace converted into a serene hotel with four acres of lush gardens. Near the Saadian Tombs — excellent for families and garden lovers.',
    rating:8.6, reviews:1320,
    gradient:'linear-gradient(135deg,#5a7a4a,#3a5030,#22301a)',
    highlight:'4-acre palace gardens',
  },
  {
    id:9, name:'Riad Farnatchi', arabic:'رياض فرناتشي',
    stars:5, pricePerNight:2200, beds:1, area:'Medina',
    distanceMedina:0.1, distanceSouk:0.3,
    tags:['Artisan','Rooftop Pool','Boutique','Design'],
    type:'Boutique Riad',
    amenities:['🏊 Rooftop Pool','☕ Terrace','🎭 Hammam','🍽️ Private Dining'],
    description:'Six interconnected riads merged into one stunning property. The rooftop plunge pool and artisan-crafted interiors make it one of the finest small hotels in Africa.',
    rating:9.3, reviews:520,
    gradient:'linear-gradient(135deg,#c4956a,#8b5e38,#5c3c1e)',
    highlight:'Rooftop plunge pool',
  },
  {
    id:10, name:'Sofitel Marrakech', arabic:'سوفيتيل مراكش',
    stars:5, pricePerNight:1400, beds:2, area:'Hivernage',
    distanceMedina:1.8, distanceSouk:2.4,
    tags:['International','Spa','Pool','Business'],
    type:'Luxury Hotel',
    amenities:['🏊 2 Pools','💆 So Spa','🍽️ 4 Restaurants','🏋️ Gym','🚗 Valet','🎭 Hammam'],
    description:'A blend of French elegance and Moroccan craftsmanship. Two large pools, the award-winning So Spa, and excellent dining make it reliable luxury.',
    rating:8.9, reviews:3210,
    gradient:'linear-gradient(135deg,#8c6090,#5c3c60,#3a2040)',
    highlight:'Award-winning So Spa',
  },
  {
    id:11, name:'Riad Be Marrakech', arabic:'رياض بي مراكش',
    stars:4, pricePerNight:750, beds:1, area:'Medina',
    distanceMedina:0.2, distanceSouk:0.4,
    tags:['Design','Minimal','Rooftop','Boutique'],
    type:'Boutique Riad',
    amenities:['☕ Rooftop Terrace','🍳 Breakfast','🎭 Hammam','📶 WiFi'],
    description:'A contemporary design riad that strips back traditional decoration to its essence. Clean lines, bold colours, and a spectacular rooftop with Atlas views.',
    rating:8.7, reviews:480,
    gradient:'linear-gradient(135deg,#9c6b4a,#6a4030,#3e2218)',
    highlight:'Atlas Mountain views',
  },
  {
    id:12, name:'Jnane Tamsna', arabic:'جنان تمسنا',
    stars:5, pricePerNight:2800, beds:3, area:'Palmeraie',
    distanceMedina:6.2, distanceSouk:6.8,
    tags:['Villa','Family','Organic','Private'],
    type:'Boutique Guesthouse',
    amenities:['🏊 3 Pools','🌿 Organic Garden','🍽️ Farm-to-Table','🚲 Bikes','🧘 Yoga'],
    description:'A collection of private villas set within an organic rose and herb garden. Bikes, yoga, and farm-to-table dinners — Marrakech at its most serene.',
    rating:9.0, reviews:390,
    gradient:'linear-gradient(135deg,#7a9c5a,#4a6a30,#2a4018)',
    highlight:'Organic rose gardens',
  },
  {
    id:13, name:'Riad Dar One', arabic:'رياض دار ون',
    stars:4, pricePerNight:480, beds:1, area:'Medina',
    distanceMedina:0.15, distanceSouk:0.25,
    tags:['Budget Friendly','Cosy','Central','Rooftop'],
    type:'Boutique Riad',
    amenities:['☕ Rooftop Terrace','🍳 Breakfast','📶 WiFi','🗺️ Tours Available'],
    description:'A welcoming small riad run by a local family. Excellent value with cosy rooms, homemade breakfast, and a rooftop where you can hear the call to prayer.',
    rating:8.5, reviews:820,
    gradient:'linear-gradient(135deg,#c4824a,#8b5020,#5c3010)',
    highlight:'Family-run warmth',
  },
  {
    id:14, name:'Tigmi', arabic:'تيغمي',
    stars:4, pricePerNight:1100, beds:2, area:'Palmeraie',
    distanceMedina:7.0, distanceSouk:7.6,
    tags:['Berber','Desert Chic','Romantic','Escape'],
    type:'Boutique Guesthouse',
    amenities:['🏊 Pool','🌴 Palm Grove','🍽️ Tagine Dinners','🎭 Hammam','🔭 Stargazing'],
    description:'A Berber-style retreat in the Palmeraie built from pisé (rammed earth). Stargazing evenings, tagine dinners under canvas, and complete digital detox.',
    rating:8.9, reviews:310,
    gradient:'linear-gradient(135deg,#c8a060,#8c6828,#5c4010)',
    highlight:'Stargazing & pisé walls',
  },
  {
    id:15, name:'Hotel Farouk', arabic:'فندق فاروق',
    stars:2, pricePerNight:180, beds:1, area:'Guéliz',
    distanceMedina:2.5, distanceSouk:3.1,
    tags:['Budget','Central','Clean','No Frills'],
    type:'Budget Hotel',
    amenities:['📶 WiFi','☕ Breakfast Option','🏨 24hr Reception'],
    description:'Clean, honest budget accommodation in the Guéliz district. Perfect for travellers who want to spend their money in the souks, not the room.',
    rating:7.6, reviews:1540,
    gradient:'linear-gradient(135deg,#7a8c7a,#506050,#303830)',
    highlight:'Best budget pick',
  },
  {
    id:16, name:'Riad Lotus Ambre', arabic:'رياض لوتس أمبر',
    stars:3, pricePerNight:320, beds:1, area:'Medina',
    distanceMedina:0.3, distanceSouk:0.5,
    tags:['Mid-Range','Medina','Riad Experience','Pool'],
    type:'Riad',
    amenities:['🏊 Small Pool','☕ Rooftop','🍳 Breakfast','📶 WiFi'],
    description:'A solid mid-range riad with authentic character, a small courtyard pool, and friendly staff. Ideal for first-time visitors who want the riad experience without palace prices.',
    rating:8.2, reviews:970,
    gradient:'linear-gradient(135deg,#c4784a,#8b4820,#5c2c0e)',
    highlight:'Authentic riad value',
  },
  {
    id:17, name:'Four Seasons Marrakech', arabic:'فور سيزونز مراكش',
    stars:5, pricePerNight:3800, beds:2, area:'Hivernage',
    distanceMedina:1.5, distanceSouk:2.0,
    tags:['Family Luxury','2 Pools','Kids Club','Fine Dining'],
    type:'Luxury Hotel',
    amenities:['🏊 2 Pools','👶 Kids Club','💆 Spa','🍽️ 3 Restaurants','🏋️ Gym','🎭 Hammam'],
    description:'The international gold standard of luxury with impeccable service, a renowned spa, children\'s programme, and two stunning pools in a lush garden setting.',
    rating:9.3, reviews:2680,
    gradient:'linear-gradient(135deg,#9a7a5a,#6a5038,#3e3020)',
    highlight:'World-class kids club',
  },
  {
    id:18, name:'Dar Bensouda', arabic:'دار بنسودة',
    stars:3, pricePerNight:410, beds:2, area:'Medina',
    distanceMedina:0.2, distanceSouk:0.35,
    tags:['Heritage','Family Rooms','Value','Authentic'],
    type:'Heritage Riad',
    amenities:['☕ Rooftop Terrace','🍳 Breakfast','🗺️ Souk Tours','📶 WiFi','🎭 Hammam'],
    description:'A beautifully restored 19th-century townhouse with family rooms and heritage tilework. The host runs guided souk walks — an exceptional cultural experience.',
    rating:8.4, reviews:420,
    gradient:'linear-gradient(135deg,#a06040,#6a3820,#3e1e0a)',
    highlight:'Guided souk walks',
  },
];

const AREAS    = ['All Areas','Medina','Hivernage','Palmeraie','Kasbah','Guéliz'];
const TYPES    = ['All Types','Palace Hotel','Luxury Hotel','Boutique Riad','Riad','Boutique Guesthouse','Boutique Hotel','Heritage Riad','Budget Hotel','Resort'];
const SORT_BY  = ['Recommended','Price: Low to High','Price: High to Low','Rating','Distance to Medina'];
const MENU_NAV = ['Our Products','Offers','Price Detection','Hotel Guide','Souk Guide','Events','Our Story'];
const MENU_FOOT= ['Contact','FAQ','Instagram','Privacy policy'];

/* ══════════════════════════════════════════════════════════════════
   UTILS
   ══════════════════════════════════════════════════════════════════ */
function useReveal() {
  const ref = useRef(null);
  const [vis, setVis] = useState(false);
  useEffect(() => {
    const obs = new IntersectionObserver(([e]) => { if (e.isIntersecting) setVis(true); }, { threshold:0.05 });
    if (ref.current) obs.observe(ref.current);
    return () => obs.disconnect();
  }, []);
  return [ref, vis];
}
function Reveal({ children, delay=0, style={} }) {
  const [ref,vis] = useReveal();
  return (
    <div ref={ref} style={{ opacity:vis?1:0,transform:vis?'translateY(0)':'translateY(22px)',transition:`opacity .65s ease ${delay}s,transform .65s ease ${delay}s`,...style }}>
      {children}
    </div>
  );
}

function Stars({ count, size=13 }) {
  return (
    <span style={{ display:'inline-flex',gap:2,alignItems:'center' }}>
      {Array.from({length:5}).map((_,i) => (
        <svg key={i} width={size} height={size} viewBox="0 0 16 16">
          <polygon points="8,1 10.2,6 15.5,6.5 11.5,10 12.8,15.3 8,12.3 3.2,15.3 4.5,10 0.5,6.5 5.8,6" fill={i<count?C.gold:'rgba(28,26,23,0.15)'} />
        </svg>
      ))}
    </span>
  );
}

function PriceTag({ price }) {
  return (
    <span>
      <span style={{ fontFamily:C.serif,fontSize:'1.7rem',fontWeight:300,color:C.dark }}>{price.toLocaleString()}</span>
      <span style={{ fontSize:'0.72rem',color:C.mid,marginLeft:4 }}>MAD / night</span>
    </span>
  );
}

/* ══════════════════════════════════════════════════════════════════
   MENU PANEL
   ══════════════════════════════════════════════════════════════════ */
function MenuPanel({ onClose }) {
  const [entered, setEntered] = useState(false);
  useEffect(() => {
    const id = requestAnimationFrame(() => requestAnimationFrame(() => setEntered(true)));
    return () => cancelAnimationFrame(id);
  }, []);
  const handleClose = () => { setEntered(false); setTimeout(onClose, 380); };
  const sel = { background:'none',border:'none',fontFamily:C.sans,fontSize:'0.75rem',color:'#888',outline:'none',cursor:'pointer',width:'100%',padding:0,appearance:'none',WebkitAppearance:'none' };
  const opts = [['Book a stay',['All Areas',...AREAS.slice(1)],1.4],['Check-In',['Select Date'],1],['Check-Out',['Select Date'],1]];
  return (
    <>
      <div onClick={handleClose} style={{ position:'fixed',inset:0,zIndex:290,backdropFilter:'blur(3px)',WebkitBackdropFilter:'blur(3px)',background:'rgba(0,0,0,0.12)',opacity:entered?1:0,transition:'opacity 0.38s ease' }}/>
      <div style={{ position:'fixed',top:0,left:0,bottom:0,zIndex:300,width:490,background:C.panel,display:'flex',flexDirection:'column',transform:entered?'translateX(0)':'translateX(-100%)',transition:'transform 0.38s cubic-bezier(0.4,0,0.2,1)',boxShadow:'6px 0 48px rgba(0,0,0,0.13)' }}>
        <div style={{ display:'flex',alignItems:'center',justifyContent:'space-between',padding:'18px 20px',flexShrink:0 }}>
          <span style={{ fontFamily:C.sans,fontWeight:700,fontSize:'1rem',color:C.dark }}>Souk&amp;Price</span>
          <button onClick={handleClose} style={{ width:38,height:38,background:'transparent',border:'1.5px solid rgba(28,26,23,0.22)',borderRadius:7,display:'flex',alignItems:'center',justifyContent:'center',cursor:'pointer',fontSize:'0.88rem',color:C.dark,transition:'background 0.2s' }}
            onMouseOver={e=>e.currentTarget.style.background='rgba(28,26,23,0.06)'}
            onMouseOut={e=>e.currentTarget.style.background='transparent'}>✕</button>
        </div>
        <nav style={{ flex:1,display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center',padding:'8px 32px',overflow:'hidden' }}>
          {MENU_NAV.map((item,i) => (
            <a key={item} href="#" onClick={handleClose}
              style={{ display:'block',width:'100%',textAlign:'center',fontFamily:C.serif,fontSize:'2.15rem',fontWeight:400,lineHeight:1.45,color:C.dark,textDecoration:'none',opacity:entered?1:0,transform:entered?'translateY(0)':'translateY(10px)',transition:`opacity 0.42s ease ${i*.05+.08}s,transform 0.42s ease ${i*.05+.08}s,color 0.2s` }}
              onMouseOver={e=>e.currentTarget.style.color=C.terra}
              onMouseOut={e=>e.currentTarget.style.color=C.dark}>{item}</a>
          ))}
        </nav>
        <div style={{ padding:'0 24px 14px',textAlign:'center',flexShrink:0,opacity:entered?1:0,transition:'opacity 0.5s ease 0.45s' }}>
          <p style={{ fontSize:'0.74rem',color:'#9c9890',lineHeight:2 }}>
            {MENU_FOOT.map((link,i)=>(
              <span key={link}>
                <a href="#" onClick={handleClose} style={{ color:'#9c9890',textDecoration:'none' }}
                  onMouseOver={e=>e.currentTarget.style.color=C.dark}
                  onMouseOut={e=>e.currentTarget.style.color='#9c9890'}>{link}</a>
                {i<MENU_FOOT.length-1&&<span style={{ margin:'0 4px' }}>,</span>}
              </span>
            ))}
          </p>
        </div>
        <div style={{ display:'flex',alignItems:'stretch',background:'white',borderTop:`1px solid ${C.border}`,height:68,flexShrink:0 }}>
          {opts.map(([label,list,flex])=>(
            <div key={label} style={{ flex,padding:'10px 16px',borderRight:label!=='Check-Out'?'1px solid #EBEBEB':'none',display:'flex',flexDirection:'column',justifyContent:'center' }}>
              <p style={{ fontSize:'0.71rem',fontWeight:600,color:C.dark,marginBottom:3 }}>{label}</p>
              <select style={sel}>{list.map(o=><option key={o}>{o}</option>)}</select>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}

/* ══════════════════════════════════════════════════════════════════
   SUBSCRIBE MODAL
   ══════════════════════════════════════════════════════════════════ */
function SubscribeModal({ onClose }) {
  const [email,setEmail]=useState('');
  const [done,setDone]=useState(false);
  return (
    <div style={{ position:'fixed',top:62,right:14,zIndex:600,width:318,background:'#c3cfd8',borderRadius:10,boxShadow:'0 16px 56px rgba(0,0,0,0.22)',overflow:'hidden' }}>
      <button onClick={onClose} style={{ position:'absolute',top:13,right:13,background:'none',border:'none',fontSize:'0.95rem',cursor:'pointer',color:C.dark }}>✕</button>
      <div style={{ padding:'26px 26px 8px',fontSize:'3.6rem',lineHeight:1 }}>🦅</div>
      <div style={{ padding:'8px 26px 26px' }}>
        {done?<p style={{ fontFamily:C.serif,fontSize:'1.1rem',fontStyle:'italic',color:C.dark }}>You're in! We'll be in touch.</p>:<>
          <p style={{ fontSize:'0.85rem',fontWeight:500,color:C.dark,marginBottom:13,lineHeight:1.5 }}>Get exclusive hotel deals in Marrakech.</p>
          <input type="email" value={email} onChange={e=>setEmail(e.target.value)} placeholder="Enter your email address"
            style={{ width:'100%',boxSizing:'border-box',background:'rgba(255,255,255,0.75)',border:'1.5px solid rgba(255,255,255,0.95)',borderRadius:5,padding:'11px 13px',fontFamily:C.sans,fontSize:'0.82rem',outline:'none',color:C.dark,marginBottom:9 }}/>
          <button onClick={()=>email&&setDone(true)} style={{ width:'100%',background:C.dark,color:'white',border:'none',borderRadius:5,padding:11,fontFamily:C.sans,fontSize:'0.74rem',letterSpacing:'0.09em',textTransform:'uppercase',cursor:'pointer',marginBottom:13 }}>Subscribe</button>
          <p style={{ fontSize:'0.73rem',color:'#3a3530',lineHeight:1.65 }}><strong>We promise we'll never spam.</strong></p>
        </>}
      </div>
    </div>
  );
}

/* ══════════════════════════════════════════════════════════════════
   FILTER SIDEBAR
   ══════════════════════════════════════════════════════════════════ */
function FilterSidebar({ filters, setFilters, resultCount, onLocate, locating, userPos }) {
  const toggle = (key, val) => {
    setFilters(f => ({ ...f, [key]: f[key]===val ? null : val }));
  };

  const ChipRow = ({ label, items, fKey, colored=false }) => (
    <div style={{ marginBottom:26 }}>
      <p style={{ fontSize:'0.62rem',letterSpacing:'0.15em',textTransform:'uppercase',color:C.mid,marginBottom:12 }}>{label}</p>
      <div style={{ display:'flex',flexWrap:'wrap',gap:7 }}>
        {items.map(item => {
          const active = filters[fKey]===item;
          return (
            <button key={item} onClick={()=>toggle(fKey,item)}
              style={{ background:active?C.dark:'white',color:active?'white':C.dark,border:`1.5px solid ${active?C.dark:C.border}`,borderRadius:20,padding:'6px 14px',fontFamily:C.sans,fontSize:'0.74rem',cursor:'pointer',transition:'all 0.2s',whiteSpace:'nowrap' }}
              onMouseOver={e=>{ if(!active){e.currentTarget.style.borderColor=C.terra;e.currentTarget.style.color=C.terra;} }}
              onMouseOut={e=>{ if(!active){e.currentTarget.style.borderColor=C.border;e.currentTarget.style.color=C.dark;} }}>
              {item}
            </button>
          );
        })}
      </div>
    </div>
  );

  const RangeRow = ({ label, fKey, min, max, step=100, prefix='', suffix=' MAD' }) => (
    <div style={{ marginBottom:26 }}>
      <div style={{ display:'flex',justifyContent:'space-between',marginBottom:10 }}>
        <p style={{ fontSize:'0.62rem',letterSpacing:'0.15em',textTransform:'uppercase',color:C.mid }}>{label}</p>
        <p style={{ fontSize:'0.72rem',color:C.terra,fontWeight:500 }}>
          {prefix}{filters[fKey+'Min']||min} – {prefix}{filters[fKey+'Max']||max}{suffix}
        </p>
      </div>
      <div style={{ display:'flex',flexDirection:'column',gap:8 }}>
        <input type="range" min={min} max={max} step={step}
          value={filters[fKey+'Min']||min}
          onChange={e=>setFilters(f=>({...f,[fKey+'Min']:Number(e.target.value)}))}
          style={{ width:'100%',accentColor:C.terra }}/>
        <input type="range" min={min} max={max} step={step}
          value={filters[fKey+'Max']||max}
          onChange={e=>setFilters(f=>({...f,[fKey+'Max']:Number(e.target.value)}))}
          style={{ width:'100%',accentColor:C.terra }}/>
      </div>
    </div>
  );

  return (
    <div style={{ background:'white',borderRadius:12,padding:'28px 24px',border:`1px solid ${C.border}`,position:'sticky',top:136 }}>
      {/* Location */}
      <div style={{ marginBottom:26,paddingBottom:26,borderBottom:`1px solid ${C.border}` }}>
        <p style={{ fontSize:'0.62rem',letterSpacing:'0.15em',textTransform:'uppercase',color:C.mid,marginBottom:12 }}>Your Location</p>
        <button onClick={onLocate} disabled={locating}
          style={{ width:'100%',background:userPos?'rgba(22,163,74,0.08)':locating?'#f5f0e8':C.terra,color:userPos?'#16a34a':locating?C.mid:'white',border:userPos?'1.5px solid rgba(22,163,74,0.3)':'none',borderRadius:8,padding:'13px 0',fontFamily:C.sans,fontSize:'0.76rem',letterSpacing:'0.08em',textTransform:'uppercase',cursor:locating?'not-allowed':'pointer',transition:'all 0.25s',display:'flex',alignItems:'center',justifyContent:'center',gap:9 }}
          onMouseOver={e=>!userPos&&!locating&&(e.currentTarget.style.background=C.terraL)}
          onMouseOut={e=>!userPos&&!locating&&(e.currentTarget.style.background=C.terra)}>
          {locating
            ? <><span style={{ width:14,height:14,border:'2px solid rgba(28,26,23,0.2)',borderTopColor:C.mid,borderRadius:'50%',display:'inline-block',animation:'spin 0.8s linear infinite' }}/>Locating…</>
            : userPos
            ? <><span>✓</span> Location Found — Showing Nearest</>
            : <><span>📍</span> Use My Location</>
          }
        </button>
        {userPos && (
          <button onClick={()=>setFilters(f=>({...f,useLocation:false}))}
            style={{ marginTop:8,width:'100%',background:'none',border:'none',fontFamily:C.sans,fontSize:'0.71rem',color:C.mid,cursor:'pointer',textAlign:'center',letterSpacing:'0.05em' }}>
            Clear location filter
          </button>
        )}
      </div>

      {/* Stars */}
      <div style={{ marginBottom:26 }}>
        <p style={{ fontSize:'0.62rem',letterSpacing:'0.15em',textTransform:'uppercase',color:C.mid,marginBottom:12 }}>Star Rating</p>
        <div style={{ display:'flex',gap:6 }}>
          {[1,2,3,4,5].map(s=>{
            const active=filters.stars===s;
            return (
              <button key={s} onClick={()=>toggle('stars',s)}
                style={{ flex:1,background:active?C.dark:'white',border:`1.5px solid ${active?C.dark:C.border}`,borderRadius:8,padding:'10px 0',cursor:'pointer',display:'flex',flexDirection:'column',alignItems:'center',gap:4,transition:'all 0.2s' }}>
                <svg width={14} height={14} viewBox="0 0 16 16"><polygon points="8,1 10.2,6 15.5,6.5 11.5,10 12.8,15.3 8,12.3 3.2,15.3 4.5,10 0.5,6.5 5.8,6" fill={active?C.gold:'rgba(28,26,23,0.2)'}/></svg>
                <span style={{ fontSize:'0.65rem',color:active?'white':C.mid,fontFamily:C.sans }}>{s}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Budget range */}
      <RangeRow label="Budget (per night)" fKey="price" min={100} max={9000} step={100}/>

      {/* Beds */}
      <div style={{ marginBottom:26 }}>
        <p style={{ fontSize:'0.62rem',letterSpacing:'0.15em',textTransform:'uppercase',color:C.mid,marginBottom:12 }}>Beds</p>
        <div style={{ display:'flex',gap:7 }}>
          {['Any',1,2,3].map(b=>{
            const active=filters.beds===(b==='Any'?null:b);
            return (
              <button key={b} onClick={()=>setFilters(f=>({...f,beds:b==='Any'?null:b}))}
                style={{ flex:1,background:active?C.dark:'white',color:active?'white':C.dark,border:`1.5px solid ${active?C.dark:C.border}`,borderRadius:8,padding:'10px 6px',fontFamily:C.sans,fontSize:'0.76rem',cursor:'pointer',transition:'all 0.2s' }}
                onMouseOver={e=>!active&&(e.currentTarget.style.borderColor=C.terra)}
                onMouseOut={e=>!active&&(e.currentTarget.style.borderColor=C.border)}>
                {b==='Any'?'Any':`${b} bed${b>1?'s':''}`}
              </button>
            );
          })}
        </div>
      </div>

      {/* Area */}
      <ChipRow label="Area" items={AREAS.slice(1)} fKey="area"/>

      {/* Type */}
      <ChipRow label="Property Type" items={TYPES.slice(1)} fKey="type"/>

      {/* Amenities */}
      <div style={{ marginBottom:26 }}>
        <p style={{ fontSize:'0.62rem',letterSpacing:'0.15em',textTransform:'uppercase',color:C.mid,marginBottom:12 }}>Must Have</p>
        <div style={{ display:'flex',flexWrap:'wrap',gap:7 }}>
          {['Pool','Spa','Restaurant','Rooftop','Breakfast','Hammam','Garden','WiFi'].map(am=>{
            const active=(filters.amenities||[]).includes(am);
            return (
              <button key={am} onClick={()=>setFilters(f=>({ ...f, amenities:active?(f.amenities||[]).filter(a=>a!==am):[...(f.amenities||[]),am] }))}
                style={{ background:active?C.terra:'white',color:active?'white':C.dark,border:`1.5px solid ${active?C.terra:C.border}`,borderRadius:20,padding:'6px 12px',fontFamily:C.sans,fontSize:'0.73rem',cursor:'pointer',transition:'all 0.2s' }}
                onMouseOver={e=>!active&&(e.currentTarget.style.borderColor=C.terra)}
                onMouseOut={e=>!active&&(e.currentTarget.style.borderColor=C.border)}>
                {am}
              </button>
            );
          })}
        </div>
      </div>

      {/* Distance to medina */}
      <div style={{ marginBottom:26 }}>
        <div style={{ display:'flex',justifyContent:'space-between',marginBottom:10 }}>
          <p style={{ fontSize:'0.62rem',letterSpacing:'0.15em',textTransform:'uppercase',color:C.mid }}>Distance to Medina</p>
          <p style={{ fontSize:'0.72rem',color:C.terra,fontWeight:500 }}>≤ {filters.maxDist||8} km</p>
        </div>
        <input type="range" min={0.1} max={8} step={0.1}
          value={filters.maxDist||8}
          onChange={e=>setFilters(f=>({...f,maxDist:Number(e.target.value)}))}
          style={{ width:'100%',accentColor:C.terra }}/>
      </div>

      {/* Clear */}
      <div style={{ paddingTop:20,borderTop:`1px solid ${C.border}` }}>
        <div style={{ display:'flex',alignItems:'center',justifyContent:'space-between',marginBottom:16 }}>
          <p style={{ fontFamily:C.serif,fontSize:'1.1rem',fontWeight:300 }}>{resultCount} hotel{resultCount!==1?'s':''} found</p>
          <button onClick={()=>setFilters({})}
            style={{ background:'none',border:'none',fontFamily:C.sans,fontSize:'0.72rem',color:C.terra,cursor:'pointer',letterSpacing:'0.06em',textDecoration:'underline' }}>
            Clear all
          </button>
        </div>
      </div>
    </div>
  );
}

/* ══════════════════════════════════════════════════════════════════
   HOTEL DETAIL MODAL
   ══════════════════════════════════════════════════════════════════ */
function HotelModal({ hotel, onClose }) {
  const [entered, setEntered] = useState(false);
  useEffect(() => {
    const id = requestAnimationFrame(() => requestAnimationFrame(() => setEntered(true)));
    document.body.style.overflow = 'hidden';
    return () => { document.body.style.overflow = ''; };
  }, []);
  const handleClose = () => { setEntered(false); setTimeout(onClose, 350); };

  return (
    <>
      <div onClick={handleClose} style={{ position:'fixed',inset:0,zIndex:800,background:'rgba(28,26,23,0.7)',backdropFilter:'blur(4px)',opacity:entered?1:0,transition:'opacity 0.35s ease' }}/>
      <div style={{ position:'fixed',top:0,right:0,bottom:0,zIndex:900,width:600,background:'white',display:'flex',flexDirection:'column',transform:entered?'translateX(0)':'translateX(100%)',transition:'transform 0.38s cubic-bezier(0.4,0,0.2,1)',overflowY:'auto',boxShadow:'-12px 0 60px rgba(0,0,0,0.2)' }}>

        {/* Hero gradient */}
        <div style={{ height:260,background:hotel.gradient,position:'relative',flexShrink:0 }}>
          <div style={{ position:'absolute',inset:0,background:'rgba(0,0,0,0.25)' }}/>
          {/* Close */}
          <button onClick={handleClose} style={{ position:'absolute',top:20,right:20,width:40,height:40,background:'rgba(255,255,255,0.15)',backdropFilter:'blur(6px)',border:'1.5px solid rgba(255,255,255,0.3)',borderRadius:8,display:'flex',alignItems:'center',justifyContent:'center',cursor:'pointer',color:'white',fontSize:'0.9rem' }}>✕</button>
          {/* Hotel name */}
          <div style={{ position:'absolute',bottom:28,left:32,right:32 }}>
            <p style={{ fontSize:'0.6rem',letterSpacing:'0.16em',textTransform:'uppercase',color:'rgba(255,255,255,0.7)',marginBottom:6 }}>{hotel.type} · {hotel.area}</p>
            <h2 style={{ fontFamily:C.serif,fontSize:'2.2rem',fontWeight:300,color:'white',lineHeight:1.15,marginBottom:6 }}>{hotel.name}</h2>
            <p style={{ fontFamily:C.serif,fontSize:'1rem',color:'rgba(255,255,255,0.6)',fontStyle:'italic' }}>{hotel.arabic}</p>
          </div>
          {/* Highlight badge */}
          <div style={{ position:'absolute',top:20,left:20,background:'rgba(181,69,27,0.85)',backdropFilter:'blur(6px)',borderRadius:20,padding:'6px 14px' }}>
            <p style={{ fontFamily:C.sans,fontSize:'0.68rem',color:'white',letterSpacing:'0.06em' }}>{hotel.highlight}</p>
          </div>
        </div>

        {/* Content */}
        <div style={{ padding:'32px 36px',flex:1 }}>
          {/* Stars + rating */}
          <div style={{ display:'flex',alignItems:'center',justifyContent:'space-between',marginBottom:20 }}>
            <Stars count={hotel.stars} size={16}/>
            <div style={{ display:'flex',alignItems:'center',gap:10 }}>
              <div style={{ background:C.dark,borderRadius:8,padding:'7px 14px' }}>
                <span style={{ fontFamily:C.sans,fontSize:'1rem',fontWeight:600,color:'white' }}>{hotel.rating}</span>
              </div>
              <div>
                <p style={{ fontSize:'0.78rem',fontWeight:500,color:C.dark }}>Exceptional</p>
                <p style={{ fontSize:'0.7rem',color:C.mid }}>{hotel.reviews.toLocaleString()} reviews</p>
              </div>
            </div>
          </div>

          {/* Price */}
          <div style={{ background:C.cream,borderRadius:10,padding:'20px 22px',marginBottom:24,display:'flex',alignItems:'center',justifyContent:'space-between' }}>
            <div>
              <p style={{ fontSize:'0.62rem',letterSpacing:'0.12em',textTransform:'uppercase',color:C.mid,marginBottom:6 }}>Price from</p>
              <PriceTag price={hotel.pricePerNight}/>
            </div>
            <div style={{ textAlign:'right' }}>
              <p style={{ fontSize:'0.7rem',color:C.mid,marginBottom:4 }}>📍 {hotel.distanceMedina} km from Medina</p>
              <p style={{ fontSize:'0.7rem',color:C.mid }}>🛍️ {hotel.distanceSouk} km from Souks</p>
            </div>
          </div>

          {/* Description */}
          <p style={{ fontSize:'0.92rem',color:C.mid,lineHeight:1.85,marginBottom:28,fontWeight:300 }}>{hotel.description}</p>

          {/* Amenities */}
          <div style={{ marginBottom:28 }}>
            <p style={{ fontSize:'0.62rem',letterSpacing:'0.15em',textTransform:'uppercase',color:C.mid,marginBottom:14 }}>Amenities</p>
            <div style={{ display:'grid',gridTemplateColumns:'1fr 1fr',gap:10 }}>
              {hotel.amenities.map((a,i)=>(
                <div key={i} style={{ display:'flex',alignItems:'center',gap:10,padding:'10px 14px',background:C.warm,borderRadius:7,border:`1px solid ${C.border}` }}>
                  <span style={{ fontSize:'1rem' }}>{a.split(' ')[0]}</span>
                  <span style={{ fontSize:'0.78rem',color:C.dark }}>{a.split(' ').slice(1).join(' ')}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Tags */}
          <div style={{ marginBottom:32 }}>
            <div style={{ display:'flex',flexWrap:'wrap',gap:7 }}>
              {hotel.tags.map((t,i)=>(
                <span key={i} style={{ background:C.cream,border:`1px solid ${C.border}`,borderRadius:20,padding:'5px 12px',fontSize:'0.72rem',color:C.mid }}>{t}</span>
              ))}
            </div>
          </div>

          {/* CTA */}
          <div style={{ display:'flex',gap:12 }}>
            <button style={{ flex:1,background:C.dark,color:'white',border:'none',borderRadius:8,padding:'16px',fontFamily:C.sans,fontSize:'0.78rem',letterSpacing:'0.1em',textTransform:'uppercase',cursor:'pointer',transition:'background 0.25s' }}
              onMouseOver={e=>e.currentTarget.style.background=C.terra}
              onMouseOut={e=>e.currentTarget.style.background=C.dark}>
              Book This Hotel
            </button>
            <button style={{ background:'white',color:C.dark,border:`1.5px solid ${C.border}`,borderRadius:8,padding:'16px 20px',fontFamily:C.sans,fontSize:'0.78rem',cursor:'pointer',transition:'all 0.2s' }}
              onMouseOver={e=>{e.currentTarget.style.borderColor=C.terra;e.currentTarget.style.color=C.terra;}}
              onMouseOut={e=>{e.currentTarget.style.borderColor=C.border;e.currentTarget.style.color=C.dark;}}>
              🗺️ Map
            </button>
          </div>
        </div>
      </div>
    </>
  );
}

/* ══════════════════════════════════════════════════════════════════
   HOTEL CARD
   ══════════════════════════════════════════════════════════════════ */
function HotelCard({ hotel, delay, onOpen, viewMode }) {
  const [hov, setHov] = useState(false);

  if (viewMode === 'list') {
    return (
      <Reveal delay={delay}>
        <div
          onMouseEnter={()=>setHov(true)} onMouseLeave={()=>setHov(false)}
          onClick={()=>onOpen(hotel)}
          style={{ background:'white',border:`1px solid ${hov?'rgba(181,69,27,0.35)':C.border}`,borderRadius:12,overflow:'hidden',cursor:'pointer',transition:'all 0.25s',display:'flex',height:160,boxShadow:hov?'0 8px 32px rgba(0,0,0,0.1)':'0 2px 8px rgba(0,0,0,0.04)' }}>
          {/* Gradient swatch */}
          <div style={{ width:160,flexShrink:0,background:hotel.gradient,position:'relative',display:'flex',alignItems:'center',justifyContent:'center' }}>
            <div style={{ position:'absolute',inset:0,background:'rgba(0,0,0,0.18)' }}/>
            <span style={{ fontSize:'2.8rem',position:'relative',zIndex:1 }}>🏨</span>
            <div style={{ position:'absolute',bottom:10,left:10,background:'rgba(181,69,27,0.85)',borderRadius:12,padding:'3px 10px' }}>
              <p style={{ fontSize:'0.62rem',color:'white',fontFamily:C.sans }}>{hotel.highlight}</p>
            </div>
          </div>
          {/* Info */}
          <div style={{ flex:1,padding:'18px 22px',display:'flex',flexDirection:'column',justifyContent:'space-between',minWidth:0 }}>
            <div>
              <div style={{ display:'flex',alignItems:'flex-start',justifyContent:'space-between',marginBottom:6 }}>
                <div>
                  <p style={{ fontSize:'0.6rem',letterSpacing:'0.13em',textTransform:'uppercase',color:C.terra,marginBottom:4 }}>{hotel.type}</p>
                  <h3 style={{ fontFamily:C.serif,fontSize:'1.35rem',fontWeight:400,color:C.dark,lineHeight:1.2 }}>{hotel.name}</h3>
                </div>
                <div style={{ textAlign:'right',flexShrink:0,marginLeft:16 }}>
                  <PriceTag price={hotel.pricePerNight}/>
                </div>
              </div>
              <Stars count={hotel.stars} size={11}/>
            </div>
            <div style={{ display:'flex',alignItems:'center',justifyContent:'space-between' }}>
              <p style={{ fontSize:'0.75rem',color:C.mid,whiteSpace:'nowrap',overflow:'hidden',textOverflow:'ellipsis',maxWidth:340 }}>
                📍 {hotel.area} · {hotel.distanceMedina} km medina · {hotel.beds} bed{hotel.beds>1?'s':''}
              </p>
              <div style={{ display:'flex',alignItems:'center',gap:8,flexShrink:0 }}>
                <div style={{ background:C.dark,borderRadius:6,padding:'4px 10px' }}>
                  <span style={{ fontFamily:C.sans,fontSize:'0.78rem',fontWeight:600,color:'white' }}>{hotel.rating}</span>
                </div>
                <span style={{ fontSize:'0.68rem',color:C.mid }}>{hotel.reviews.toLocaleString()} reviews</span>
              </div>
            </div>
          </div>
        </div>
      </Reveal>
    );
  }

  // Grid card
  return (
    <Reveal delay={delay}>
      <div
        onMouseEnter={()=>setHov(true)} onMouseLeave={()=>setHov(false)}
        onClick={()=>onOpen(hotel)}
        style={{ background:'white',border:`1px solid ${hov?'rgba(181,69,27,0.35)':C.border}`,borderRadius:12,overflow:'hidden',cursor:'pointer',transition:'all 0.28s',boxShadow:hov?'0 12px 40px rgba(0,0,0,0.12)':'0 2px 10px rgba(0,0,0,0.05)',transform:hov?'translateY(-3px)':'translateY(0)' }}>
        {/* Gradient hero */}
        <div style={{ height:160,background:hotel.gradient,position:'relative',display:'flex',alignItems:'flex-end',padding:'16px' }}>
          <div style={{ position:'absolute',inset:0,background:'rgba(0,0,0,0.2)' }}/>
          {/* Top badges */}
          <div style={{ position:'absolute',top:12,left:12,right:12,display:'flex',justifyContent:'space-between',alignItems:'flex-start' }}>
            <div style={{ background:'rgba(181,69,27,0.85)',backdropFilter:'blur(4px)',borderRadius:12,padding:'4px 10px' }}>
              <p style={{ fontSize:'0.62rem',color:'white',fontFamily:C.sans,lineHeight:1.2 }}>{hotel.highlight}</p>
            </div>
            <div style={{ background:'rgba(28,26,23,0.75)',backdropFilter:'blur(4px)',borderRadius:8,padding:'5px 10px' }}>
              <span style={{ fontFamily:C.sans,fontSize:'0.8rem',fontWeight:600,color:'white' }}>{hotel.rating}</span>
            </div>
          </div>
          {/* Bottom: name */}
          <div style={{ position:'relative',zIndex:1 }}>
            <p style={{ fontSize:'0.58rem',letterSpacing:'0.14em',textTransform:'uppercase',color:'rgba(255,255,255,0.65)',marginBottom:4 }}>{hotel.type}</p>
            <h3 style={{ fontFamily:C.serif,fontSize:'1.3rem',fontWeight:400,color:'white',lineHeight:1.2 }}>{hotel.name}</h3>
          </div>
        </div>

        {/* Body */}
        <div style={{ padding:'18px 20px' }}>
          <div style={{ display:'flex',alignItems:'center',justifyContent:'space-between',marginBottom:10 }}>
            <Stars count={hotel.stars} size={12}/>
            <span style={{ fontSize:'0.68rem',color:C.mid }}>{hotel.reviews.toLocaleString()} reviews</span>
          </div>

          <p style={{ fontSize:'0.78rem',color:C.mid,lineHeight:1.65,marginBottom:14,display:'-webkit-box',WebkitLineClamp:2,WebkitBoxOrient:'vertical',overflow:'hidden' }}>
            {hotel.description}
          </p>

          {/* Meta row */}
          <div style={{ display:'flex',gap:14,marginBottom:14,flexWrap:'wrap' }}>
            {[`📍 ${hotel.area}`,`🚶 ${hotel.distanceMedina}km`,`🛏️ ${hotel.beds} bed${hotel.beds>1?'s':''}`].map((m,i)=>(
              <span key={i} style={{ fontSize:'0.69rem',color:C.mid,display:'flex',alignItems:'center',gap:3 }}>{m}</span>
            ))}
          </div>

          {/* Tags */}
          <div style={{ display:'flex',gap:5,flexWrap:'wrap',marginBottom:16 }}>
            {hotel.tags.slice(0,3).map((t,i)=>(
              <span key={i} style={{ background:C.cream,border:`1px solid ${C.border}`,borderRadius:12,padding:'3px 9px',fontSize:'0.66rem',color:C.mid }}>{t}</span>
            ))}
          </div>

          {/* Price + CTA */}
          <div style={{ display:'flex',alignItems:'center',justifyContent:'space-between',paddingTop:14,borderTop:`1px solid ${C.border}` }}>
            <PriceTag price={hotel.pricePerNight}/>
            <div style={{ background:hov?C.terra:C.dark,color:'white',borderRadius:7,padding:'9px 18px',fontFamily:C.sans,fontSize:'0.71rem',letterSpacing:'0.08em',textTransform:'uppercase',transition:'background 0.25s' }}>
              View →
            </div>
          </div>
        </div>
      </div>
    </Reveal>
  );
}

/* ══════════════════════════════════════════════════════════════════
   MAIN PAGE
   ══════════════════════════════════════════════════════════════════ */
export default function HotelHelper() {
  const [showMenu,      setShowMenu]      = useState(false);
  const [showSubscribe, setShowSubscribe] = useState(false);
  const [filters,       setFilters]       = useState({});
  const [sortBy,        setSortBy]        = useState('Recommended');
  const [viewMode,      setViewMode]      = useState('grid'); // grid | list
  const [userPos,       setUserPos]       = useState(null);
  const [locating,      setLocating]      = useState(false);
  const [selectedHotel, setSelectedHotel] = useState(null);
  const [loaded,        setLoaded]        = useState(false);
  const [searchQuery,   setSearchQuery]   = useState('');

  useEffect(() => { setTimeout(() => setLoaded(true), 60); }, []);

  /* ── Geolocation ── */
  const locateMe = () => {
    setLocating(true);
    navigator.geolocation.getCurrentPosition(
      p => { setUserPos({ lat:p.coords.latitude, lng:p.coords.longitude }); setLocating(false); setFilters(f=>({...f,useLocation:true})); },
      () => setLocating(false),
      { enableHighAccuracy:true, timeout:10000 }
    );
  };

  /* ── Filter + sort logic ── */
  const filtered = HOTELS.filter(h => {
    if (filters.stars    && h.stars !== filters.stars) return false;
    if (filters.area     && h.area !== filters.area)   return false;
    if (filters.type     && h.type !== filters.type)   return false;
    if (filters.beds     && h.beds !== filters.beds)   return false;
    if (filters.priceMin && h.pricePerNight < filters.priceMin) return false;
    if (filters.priceMax && h.pricePerNight > filters.priceMax) return false;
    if (filters.maxDist  && h.distanceMedina > filters.maxDist) return false;
    if (filters.amenities && filters.amenities.length > 0) {
      const amenStr = h.amenities.join(' ') + ' ' + h.tags.join(' ');
      if (!filters.amenities.every(a => amenStr.toLowerCase().includes(a.toLowerCase()))) return false;
    }
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      if (!h.name.toLowerCase().includes(q) && !h.area.toLowerCase().includes(q) && !h.type.toLowerCase().includes(q) && !h.description.toLowerCase().includes(q)) return false;
    }
    return true;
  }).sort((a,b) => {
    if (sortBy==='Price: Low to High')   return a.pricePerNight - b.pricePerNight;
    if (sortBy==='Price: High to Low')   return b.pricePerNight - a.pricePerNight;
    if (sortBy==='Rating')               return b.rating - a.rating;
    if (sortBy==='Distance to Medina')   return a.distanceMedina - b.distanceMedina;
    // Recommended: by rating * reviews weight
    return (b.rating * Math.log(b.reviews)) - (a.rating * Math.log(a.reviews));
  });

  const sel = { background:'none',border:'none',fontFamily:C.sans,fontSize:'0.76rem',color:C.mid,outline:'none',cursor:'pointer',padding:0,appearance:'none',WebkitAppearance:'none' };

  return (
    <div style={{ fontFamily:C.sans,background:C.cream,color:C.dark,minHeight:'100vh',overflowX:'hidden' }}>
      <FontLink/>

      {/* ══ HEADER ══ */}
      <header style={{ position:'fixed',top:0,left:0,right:0,zIndex:200 }}>
        <div style={{ display:'flex',alignItems:'center',justifyContent:'space-between',padding:'12px 16px',background:'rgba(245,240,232,0.97)',backdropFilter:'blur(12px)' }}>
          <div style={{ display:'flex',alignItems:'center',gap:8 }}>
            <a href="/" style={{ background:'white',borderRadius:8,padding:'9px 18px',boxShadow:'0 1px 6px rgba(0,0,0,0.07)',textDecoration:'none' }}>
              <span style={{ fontFamily:C.sans,fontWeight:700,fontSize:'0.98rem',letterSpacing:'-0.01em',color:C.dark }}>Souk&amp;Price</span>
            </a>
            <button onClick={()=>setShowMenu(m=>!m)}
              style={{ background:'white',border:'none',borderRadius:8,width:42,height:42,cursor:'pointer',boxShadow:'0 1px 6px rgba(0,0,0,0.07)',display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center',gap:4.5 }}>
              {[0,1,2].map(i=><span key={i} style={{ display:'block',width:17,height:1.5,background:C.dark,borderRadius:2 }}/>)}
            </button>
          </div>
          {/* Breadcrumb */}
          <div style={{ position:'absolute',left:'50%',transform:'translateX(-50%)',display:'flex',alignItems:'center',gap:8 }}>
            <span style={{ fontSize:'0.76rem',color:C.mid }}>Marrakech</span>
            <span style={{ width:4,height:4,borderRadius:'50%',background:C.terra }}/>
            <span style={{ fontSize:'0.76rem',color:C.terra,fontWeight:500 }}>Hotel Guide</span>
          </div>
          <div style={{ display:'flex',gap:8 }}>
            {['Enquiries','Subscribe'].map(label=>(
              <button key={label} onClick={label==='Subscribe'?()=>setShowSubscribe(s=>!s):undefined}
                style={{ background:'white',color:C.dark,border:'none',borderRadius:22,padding:'9px 20px',fontFamily:C.sans,fontSize:'0.82rem',cursor:'pointer',boxShadow:'0 1px 6px rgba(0,0,0,0.07)',transition:'box-shadow .2s' }}
                onMouseOver={e=>e.currentTarget.style.boxShadow='0 3px 14px rgba(0,0,0,0.13)'}
                onMouseOut={e=>e.currentTarget.style.boxShadow='0 1px 6px rgba(0,0,0,0.07)'}>{label}</button>
            ))}
          </div>
        </div>

        {/* Search + booking bar */}
        <div style={{ display:'flex',alignItems:'stretch',background:'white',borderRadius:10,margin:'0 16px 12px',boxShadow:'0 2px 14px rgba(0,0,0,0.09)',overflow:'hidden',height:58 }}>
          {/* Search input */}
          <div style={{ flex:2,padding:'10px 20px',borderRight:'1px solid #EBEBEB',display:'flex',alignItems:'center',gap:10 }}>
            <span style={{ fontSize:'1rem',flexShrink:0 }}>🔍</span>
            <input type="text" placeholder="Search hotels, areas, types…" value={searchQuery} onChange={e=>setSearchQuery(e.target.value)}
              style={{ flex:1,border:'none',outline:'none',fontFamily:C.sans,fontSize:'0.82rem',color:C.dark,background:'none' }}/>
            {searchQuery && <button onClick={()=>setSearchQuery('')} style={{ background:'none',border:'none',cursor:'pointer',color:C.mid,fontSize:'0.9rem' }}>✕</button>}
          </div>
          <div style={{ flex:1,padding:'10px 20px',borderRight:'1px solid #EBEBEB',display:'flex',flexDirection:'column',justifyContent:'center' }}>
            <p style={{ fontSize:'0.73rem',fontWeight:600,color:C.dark,marginBottom:2 }}>Sort by</p>
            <select value={sortBy} onChange={e=>setSortBy(e.target.value)} style={sel}>{SORT_BY.map(s=><option key={s}>{s}</option>)}</select>
          </div>
          <div style={{ flex:1,padding:'10px 20px',borderRight:'1px solid #EBEBEB',display:'flex',flexDirection:'column',justifyContent:'center' }}>
            <p style={{ fontSize:'0.73rem',fontWeight:600,color:C.dark,marginBottom:2 }}>Area</p>
            <select value={filters.area||'All Areas'} onChange={e=>setFilters(f=>({...f,area:e.target.value==='All Areas'?null:e.target.value}))} style={sel}>{AREAS.map(a=><option key={a}>{a}</option>)}</select>
          </div>
          <button style={{ background:C.dark,color:'white',border:'none',padding:'0 28px',fontFamily:C.sans,fontSize:'0.76rem',letterSpacing:'0.09em',textTransform:'uppercase',cursor:'pointer',whiteSpace:'nowrap',transition:'background .25s' }}
            onMouseOver={e=>e.currentTarget.style.background=C.terra}
            onMouseOut={e=>e.currentTarget.style.background=C.dark}>Search</button>
        </div>
      </header>

      {showMenu      && <MenuPanel onClose={()=>setShowMenu(false)}/>}
      {showSubscribe && <SubscribeModal onClose={()=>setShowSubscribe(false)}/>}
      {selectedHotel && <HotelModal hotel={selectedHotel} onClose={()=>setSelectedHotel(null)}/>}

      {/* ══ HERO ══ */}
      <div style={{ paddingTop:132,background:`linear-gradient(180deg,${C.cream} 0%,${C.warm} 100%)` }}>
        <div style={{ maxWidth:1440,margin:'0 auto',padding:'52px 80px 0' }}>
          <div style={{ display:'grid',gridTemplateColumns:'1fr auto',alignItems:'flex-end',gap:40,marginBottom:52 }}>
            <div>
              <div style={{ opacity:loaded?1:0,transform:loaded?'translateY(0)':'translateY(16px)',transition:'opacity 0.6s ease 0.1s,transform 0.6s ease 0.1s' }}>
                <p style={{ fontSize:'0.63rem',letterSpacing:'0.2em',textTransform:'uppercase',color:C.terra,marginBottom:14 }}>Marrakech · 18 Curated Hotels</p>
              </div>
              <div style={{ opacity:loaded?1:0,transform:loaded?'translateY(0)':'translateY(16px)',transition:'opacity 0.6s ease 0.2s,transform 0.6s ease 0.2s' }}>
                <h1 style={{ fontFamily:C.serif,fontSize:'clamp(2.8rem,4.2vw,4.6rem)',fontWeight:300,lineHeight:1.05,color:C.dark,marginBottom:16 }}>
                  Find your riad,<br/><em style={{ fontStyle:'italic',color:C.terra }}>in the heart of the medina.</em>
                </h1>
              </div>
              <div style={{ opacity:loaded?1:0,transform:loaded?'translateY(0)':'translateY(16px)',transition:'opacity 0.6s ease 0.3s,transform 0.6s ease 0.3s' }}>
                <p style={{ fontSize:'1rem',fontWeight:300,color:C.mid,lineHeight:1.8,maxWidth:520 }}>
                  From legendary palace hotels to intimate family riads — every accommodation in Marrakech, filtered by what matters to you.
                </p>
              </div>
            </div>
            {/* Quick stats */}
            <div style={{ display:'grid',gridTemplateColumns:'1fr 1fr',gap:8,opacity:loaded?1:0,transition:'opacity 0.6s ease 0.4s' }}>
              {[{n:'18',l:'Curated Hotels'},{n:'5',l:'Areas Covered'},{n:'★5',l:'Palace Hotels'},{n:'MAD',l:'All budgets'}].map((s,i)=>(
                <div key={i} style={{ background:'white',borderRadius:10,padding:'16px 18px',boxShadow:'0 2px 12px rgba(0,0,0,0.06)',border:`1px solid ${C.border}`,textAlign:'center' }}>
                  <p style={{ fontFamily:C.serif,fontSize:'1.6rem',fontWeight:300,color:C.terra,marginBottom:2 }}>{s.n}</p>
                  <p style={{ fontSize:'0.68rem',color:C.mid,letterSpacing:'0.06em' }}>{s.l}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Area pills */}
          <div style={{ display:'flex',gap:8,marginBottom:0,flexWrap:'wrap',opacity:loaded?1:0,transition:'opacity 0.6s ease 0.5s' }}>
            {AREAS.map(area=>{
              const active=filters.area===(area==='All Areas'?null:area)||(area==='All Areas'&&!filters.area);
              return (
                <button key={area}
                  onClick={()=>setFilters(f=>({...f,area:area==='All Areas'?null:area}))}
                  style={{ background:active?C.dark:'white',color:active?'white':C.dark,border:`1.5px solid ${active?C.dark:C.border}`,borderRadius:22,padding:'9px 20px',fontFamily:C.sans,fontSize:'0.78rem',cursor:'pointer',transition:'all 0.2s',boxShadow:active?'0 4px 14px rgba(28,26,23,0.18)':'0 1px 4px rgba(0,0,0,0.06)' }}
                  onMouseOver={e=>!active&&(e.currentTarget.style.borderColor=C.terra)}
                  onMouseOut={e=>!active&&(e.currentTarget.style.borderColor=C.border)}>
                  {area}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* ══ MAIN CONTENT ══ */}
      <div style={{ maxWidth:1440,margin:'0 auto',padding:'40px 80px 100px',display:'grid',gridTemplateColumns:'300px 1fr',gap:32,alignItems:'start' }}>

        {/* ── Filters ── */}
        <FilterSidebar
          filters={filters}
          setFilters={setFilters}
          resultCount={filtered.length}
          onLocate={locateMe}
          locating={locating}
          userPos={userPos}
        />

        {/* ── Hotel Grid / List ── */}
        <div>
          {/* Toolbar */}
          <div style={{ display:'flex',alignItems:'center',justifyContent:'space-between',marginBottom:24 }}>
            <div>
              <span style={{ fontFamily:C.serif,fontSize:'1.4rem',fontWeight:300,color:C.dark }}>{filtered.length}</span>
              <span style={{ fontSize:'0.8rem',color:C.mid,marginLeft:8 }}>hotel{filtered.length!==1?'s':''} match your search</span>
              {userPos && <span style={{ fontSize:'0.72rem',color:C.terra,marginLeft:12,background:'rgba(181,69,27,0.08)',border:'1px solid rgba(181,69,27,0.2)',borderRadius:12,padding:'3px 10px' }}>📍 Nearest first</span>}
            </div>
            <div style={{ display:'flex',alignItems:'center',gap:8 }}>
              {/* View toggle */}
              {['grid','list'].map(mode=>(
                <button key={mode} onClick={()=>setViewMode(mode)}
                  style={{ width:36,height:36,background:viewMode===mode?C.dark:'white',border:`1.5px solid ${viewMode===mode?C.dark:C.border}`,borderRadius:7,display:'flex',alignItems:'center',justifyContent:'center',cursor:'pointer',transition:'all 0.2s',fontSize:'0.9rem' }}>
                  {mode==='grid'?'⊞':'☰'}
                </button>
              ))}
            </div>
          </div>

          {/* Featured spotlight — top 1 */}
          {filtered.length > 0 && sortBy === 'Recommended' && !searchQuery && Object.keys(filters).filter(k=>filters[k]).length === 0 && (
            <Reveal delay={0}>
              <div onClick={()=>setSelectedHotel(filtered[0])} style={{ background:filtered[0].gradient,borderRadius:14,padding:'0',marginBottom:24,overflow:'hidden',cursor:'pointer',position:'relative',height:240,display:'flex',alignItems:'flex-end' }}>
                <div style={{ position:'absolute',inset:0,background:'linear-gradient(to top,rgba(0,0,0,0.7) 0%,rgba(0,0,0,0.1) 60%)' }}/>
                <div style={{ position:'absolute',top:18,left:18,background:'rgba(181,69,27,0.9)',backdropFilter:'blur(4px)',borderRadius:20,padding:'6px 16px' }}>
                  <p style={{ fontFamily:C.sans,fontSize:'0.65rem',color:'white',letterSpacing:'0.08em',textTransform:'uppercase' }}>✦ Editor's Pick</p>
                </div>
                <div style={{ position:'absolute',top:18,right:18,background:'rgba(28,26,23,0.75)',backdropFilter:'blur(4px)',borderRadius:8,padding:'6px 12px',display:'flex',alignItems:'center',gap:6 }}>
                  <span style={{ fontFamily:C.sans,fontSize:'0.9rem',fontWeight:600,color:'white' }}>{filtered[0].rating}</span>
                  <Stars count={filtered[0].stars} size={11}/>
                </div>
                <div style={{ position:'relative',padding:'28px 32px',zIndex:1,display:'flex',alignItems:'flex-end',justifyContent:'space-between',width:'100%' }}>
                  <div>
                    <p style={{ fontSize:'0.6rem',letterSpacing:'0.15em',textTransform:'uppercase',color:'rgba(255,255,255,0.65)',marginBottom:6 }}>{filtered[0].type} · {filtered[0].area}</p>
                    <h3 style={{ fontFamily:C.serif,fontSize:'2rem',fontWeight:300,color:'white',marginBottom:6 }}>{filtered[0].name}</h3>
                    <p style={{ fontSize:'0.8rem',color:'rgba(255,255,255,0.75)',maxWidth:500 }}>{filtered[0].highlight}</p>
                  </div>
                  <div style={{ textAlign:'right',flexShrink:0,marginLeft:24 }}>
                    <p style={{ fontFamily:C.serif,fontSize:'1.8rem',fontWeight:300,color:'white' }}>{filtered[0].pricePerNight.toLocaleString()}</p>
                    <p style={{ fontSize:'0.7rem',color:'rgba(255,255,255,0.65)' }}>MAD / night</p>
                    <div style={{ marginTop:10,background:'white',borderRadius:7,padding:'9px 20px',display:'inline-block' }}>
                      <span style={{ fontFamily:C.sans,fontSize:'0.72rem',fontWeight:600,color:C.dark,letterSpacing:'0.08em',textTransform:'uppercase' }}>View Hotel →</span>
                    </div>
                  </div>
                </div>
              </div>
            </Reveal>
          )}

          {/* Hotel cards */}
          {filtered.length === 0 ? (
            <div style={{ background:'white',borderRadius:12,padding:'80px 40px',textAlign:'center',border:`1px solid ${C.border}` }}>
              <div style={{ fontSize:'3.5rem',marginBottom:20 }}>🏨</div>
              <p style={{ fontFamily:C.serif,fontSize:'1.6rem',fontWeight:300,color:C.dark,marginBottom:10 }}>No hotels match your filters</p>
              <p style={{ fontSize:'0.85rem',color:C.mid,marginBottom:24 }}>Try adjusting your budget range, stars, or area to see more results.</p>
              <button onClick={()=>setFilters({})} style={{ background:C.terra,color:'white',border:'none',borderRadius:8,padding:'13px 28px',fontFamily:C.sans,fontSize:'0.76rem',letterSpacing:'0.1em',textTransform:'uppercase',cursor:'pointer' }}>Reset Filters</button>
            </div>
          ) : viewMode === 'grid' ? (
            <div style={{ display:'grid',gridTemplateColumns:'repeat(2,1fr)',gap:18 }}>
              {(sortBy==='Recommended'&&!searchQuery&&Object.keys(filters).filter(k=>filters[k]).length===0 ? filtered.slice(1) : filtered).map((h,i)=>(
                <HotelCard key={h.id} hotel={h} delay={i*0.04} onOpen={setSelectedHotel} viewMode="grid"/>
              ))}
            </div>
          ) : (
            <div style={{ display:'flex',flexDirection:'column',gap:12 }}>
              {filtered.map((h,i)=>(
                <HotelCard key={h.id} hotel={h} delay={i*0.03} onOpen={setSelectedHotel} viewMode="list"/>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* ══ NEWSLETTER ══ */}
      <div style={{ background:C.terra,padding:'90px 80px',textAlign:'center' }}>
        <Reveal><h2 style={{ fontFamily:C.serif,fontSize:'clamp(2.2rem,4vw,3.8rem)',fontWeight:300,color:'white',lineHeight:1.1,marginBottom:14 }}>Stay in <em style={{ fontStyle:'italic' }}>the right riad.</em></h2></Reveal>
        <Reveal delay={0.1}><p style={{ color:'rgba(255,255,255,0.75)',fontSize:'0.93rem',fontWeight:300,marginBottom:44 }}>Get curated hotel deals, seasonal offers and souk guides delivered to your inbox.</p></Reveal>
        <Reveal delay={0.2}>
          <div style={{ display:'flex',maxWidth:460,margin:'0 auto' }}>
            <input type="email" placeholder="Your email address"
              style={{ flex:1,background:'rgba(255,255,255,0.15)',border:'1px solid rgba(255,255,255,0.3)',borderRight:'none',padding:'15px 20px',color:'white',fontFamily:C.sans,fontSize:'0.88rem',outline:'none',borderRadius:'2px 0 0 2px' }}/>
            <button style={{ background:'white',color:C.terra,border:'none',padding:'15px 26px',fontFamily:C.sans,fontSize:'0.72rem',letterSpacing:'0.1em',textTransform:'uppercase',cursor:'pointer',fontWeight:500,borderRadius:'0 2px 2px 0' }}>Subscribe</button>
          </div>
        </Reveal>
      </div>

      {/* ══ FOOTER ══ */}
      <footer style={{ background:C.dark,padding:'50px 80px 28px' }}>
        <div style={{ maxWidth:1440,margin:'0 auto',display:'flex',justifyContent:'space-between',alignItems:'center',borderTop:'1px solid rgba(255,255,255,0.07)',paddingTop:20 }}>
          <span style={{ fontFamily:C.serif,fontSize:'1.1rem',color:'white' }}>Souk <span style={{ color:C.terra }}>&</span> Price</span>
          <span style={{ fontSize:'0.69rem',color:'#5c5549' }}>Hotel data curated by our Marrakech team · 2025</span>
          <span style={{ fontSize:'0.69rem',color:'#5c5549' }}>© 2025 Souk & Price</span>
        </div>
      </footer>

      <style>{`
        *{box-sizing:border-box;margin:0;padding:0;}
        html{scroll-behavior:smooth;}
        select,input{font-family:'Jost',sans-serif;}
        select{-webkit-appearance:none;-moz-appearance:none;appearance:none;}
        @keyframes spin{to{transform:rotate(360deg)}}
        input::placeholder{color:rgba(92,85,73,0.5);}
        input::-webkit-input-placeholder{color:rgba(92,85,73,0.5);}
        input[type=range]{-webkit-appearance:none;height:3px;border-radius:2px;background:rgba(28,26,23,0.12);outline:none;}
        input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:16px;height:16px;border-radius:50%;background:#B5451B;cursor:pointer;border:2px solid white;box-shadow:0 1px 6px rgba(181,69,27,0.35);}
      `}</style>
    </div>
  );
}