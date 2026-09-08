// Minimal DOM: the game only needs a canvas-shaped object and a few elements.
// render() is never called by the harness, so 2D context calls just need to exist.
const noop = () => {};
function ctxStub(){
  return new Proxy({}, { get: (t,k) => {
    if(k === 'canvas') return { width: 1600, height: 900 };
    if(k === 'measureText') return () => ({ width: 10 });
    if(k === 'createLinearGradient' || k === 'createRadialGradient' || k === 'createPattern')
      return () => ({ addColorStop: noop });
    if(k === 'getImageData') return () => ({ data: new Uint8ClampedArray(4) });
    return noop;
  }, set: () => true });
}
function elStub(id){
  const el = {
    id, width:1600, height:900, textContent:'', innerHTML:'', value:'',
    style: new Proxy({}, { get:(t,k)=> k==='setProperty'? noop : '', set:()=>true }),
    classList: { add:noop, remove:noop, toggle:noop, contains:()=>false },
    dataset: {},
    getContext: () => ctxStub(),
    addEventListener: noop, removeEventListener: noop,
    getBoundingClientRect: () => ({ left:0, top:0, width:1600, height:900, right:1600, bottom:900 }),
    appendChild: noop, removeChild: noop, querySelector: ()=>elStub('q'),
    querySelectorAll: ()=>[], getElementsByClassName: ()=>[], setAttribute: noop, focus: noop, click: noop,
    remove: noop, insertBefore: noop,
    offsetWidth: 16, offsetHeight: 32, childElementCount: 0, firstChild: null, children: []
  };
  Object.defineProperty(el, 'parentElement', { get: () => el });
  Object.defineProperty(el, 'parentNode',    { get: () => el });
  return el;
}
globalThis.addEventListener = noop;
globalThis.removeEventListener = noop;
globalThis.dispatchEvent = () => true;
globalThis.window = globalThis;
const _cache = new Map();
function el(id){ if(!_cache.has(id)) _cache.set(id, elStub(id)); return _cache.get(id); }
globalThis.document = {
  getElementById: (id) => el(id),
  createElement: (t) => elStub(t),
  querySelector: () => elStub('q'),
  querySelectorAll: () => [],
  addEventListener: noop, removeEventListener: noop, dispatchEvent: ()=>true,
  body: el('body'), documentElement: el('html'),
  fonts: { ready: Promise.resolve(), addEventListener: noop }
};
globalThis.navigator = { userAgent:'node', maxTouchPoints:0 };
globalThis.performance = globalThis.performance || { now: () => Date.now() };
globalThis.requestAnimationFrame = () => 0;
globalThis.cancelAnimationFrame = noop;
globalThis.ResizeObserver = class { observe(){} disconnect(){} };
globalThis.Image = class { constructor(){ this.onload=null; } set src(v){} };
globalThis.matchMedia = () => ({ matches:false, addEventListener:noop });
globalThis.localStorage = { getItem:()=>null, setItem:noop };
globalThis.Path2D = class {};
globalThis.Touch = class {}; globalThis.TouchEvent = class {};
globalThis.KeyboardEvent = class {}; globalThis.MouseEvent = class {};
globalThis.Event = class { constructor(t){ this.type=t; } };

// The game starts a 400ms layout-refresh setInterval at load and a few short
// setTimeouts during play (tooltip auto-hide, HUD flash). Harmless in a
// browser, but under Node an active timer keeps the event loop alive, so a sim
// script would print its report and then hang until killed.
//
// Timers created while GAME code is running are therefore unref'd: they still
// exist and can be cleared, they just never hold the process open, so Node
// exits as soon as a script's own work is done. harness.js raises __laneInGame
// while it evaluates the game script and for the duration of every start(),
// step() and state() call. A timer a sim script creates for itself, outside
// those calls, is the real thing and fires as normal — so a script can still
// await a delay without the harness silently swallowing it.
globalThis.__laneInGame = 0;
for(const name of ['setTimeout', 'setInterval']){
  const real = globalThis[name];
  globalThis[name] = function(fn, ms, ...args){
    if(!(globalThis.__laneInGame > 0)) return real(fn, ms, ...args);
    // anything scheduled from inside a game timer's callback is game code too
    const inGame = (...a) => {
      globalThis.__laneInGame++;
      try { return fn(...a); } finally { globalThis.__laneInGame--; }
    };
    return real(inGame, ms, ...args).unref();
  };
}
