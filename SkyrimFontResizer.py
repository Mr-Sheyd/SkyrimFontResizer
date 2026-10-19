# -*- coding: utf-8 -*-
"""
Skyrim Font Resizer — GUI for resizing Skyrim SWF fonts (DefineFont3).
Drag an SWF into the window (or click "Open…"), review the original sizes,
enter a multiplier or desired letter height, and click "Save…".
"""
import math, os, struct, sys, threading, zlib, traceback
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
    HAVE_DND = True
except Exception:
    HAVE_DND = False

EM = 20480

# ========================== localization ==========================
LANG = {
    'en': {
        'drop_dnd':         'Drag an SWF font file here (or click "Open…")',
        'drop_no_dnd':      'Click "Open…" and select an SWF font file',
        'btn_open':         'Open…',
        'file_none':        'No file selected',
        'file_info':        '{name} — fonts: {n}{extra}',
        'file_extra':       ' (fonts in unsupported format: {n})',
        'col_name':         'Font',
        'col_glyphs':       'Glyphs',
        'col_cyr':          'Cyrillic',
        'col_cap':          '"H", %',
        'col_xh':           '"x", %',
        'col_k':            'Multiplier',
        'col_ncap':         'New "H", %',
        'col_nxh':          'New "x", %',
        'cyr_yes':          'yes',
        'cyr_no':           'no',
        'frame_size':       ' Size of selected fonts (Ctrl/Shift — multi-select) ',
        'lbl_k':            'Multiplier:',
        'lbl_cap':          'or "H" height, %:',
        'lbl_xh':           'or "x" height, %:',
        'btn_reset':        'Reset all',
        'vanilla_hint':     'For reference, vanilla (fonts_ru.swf, FuturaTCYLigCon): "H" ≈ 66.7%, "x" ≈ 45.3%',
        'frame_preview':    ' Preview (contours, same point size): top = original, bottom = scaled ',
        'btn_save':         'Save…',
        'status_ready':     'Ready.',
        'status_select':    'Select a font in the table and enter a multiplier or target letter height.',
        'status_working':   'Processing… (large fonts may take a few seconds)',
        'status_error':     'Error.',
        'status_saved':     'Saved: {path}',
        'preview_was':      'original',
        'preview_will':     'scaled ×%.3f',
        'err_open_title':   'Failed to open',
        'err_no_fonts_title': 'No fonts',
        'err_no_fonts':     'The file contains no DefineFont3 fonts. This is not a Skyrim font library, or the format is unsupported.',
        'err_nothing_title': 'Nothing to save',
        'err_nothing':      'All multipliers are 1.0. Change the size of at least one font.',
        'dlg_save_title':   'Save as (better keep the original filename)',
        'dlg_open_title':   'Select an SWF with fonts',
        'ft_swf':           'SWF',
        'ft_all':           'All files',
        'done_title':       'Done',
        'done_msg':         'Saved:\n%s\n\nChanged: %s\n\nPlace the file in a mod at Interface\\%s with priority above the original.',
        'err_not_swf':      'This is not an SWF file.',
        'err_lzma':         'SWF with LZMA compression (ZWS) is not supported.',
    },
    'ru': {
        'drop_dnd':         'Перетащи сюда SWF-файл со шрифтами (или нажми «Открыть…»)',
        'drop_no_dnd':      'Нажми «Открыть…» и выбери SWF-файл со шрифтами',
        'btn_open':         'Открыть…',
        'file_none':        'Файл не выбран',
        'file_info':        '{name} — шрифтов: {n}{extra}',
        'file_extra':       ' (шрифтов в неподдерживаемом формате: {n})',
        'col_name':         'Шрифт',
        'col_glyphs':       'Глифов',
        'col_cyr':          'Кириллица',
        'col_cap':          '«Н», %',
        'col_xh':           '«х», %',
        'col_k':            'Множитель',
        'col_ncap':         'Новая «Н», %',
        'col_nxh':          'Новая «х», %',
        'cyr_yes':          'да',
        'cyr_no':           'нет',
        'frame_size':       ' Размер выбранных шрифтов (Ctrl/Shift — несколько) ',
        'lbl_k':            'Множитель:',
        'lbl_cap':          'или высота «Н», %:',
        'lbl_xh':           'или высота «х», %:',
        'btn_reset':        'Сбросить всё',
        'vanilla_hint':     'Для сравнения, ваниль (fonts_ru.swf, FuturaTCYLigCon): «Н» ≈ 66.7%, «х» ≈ 45.3%',
        'frame_preview':    ' Предпросмотр (контуры, один и тот же кегль): сверху было, снизу будет ',
        'btn_save':         'Сохранить…',
        'status_ready':     'Готов.',
        'status_select':    'Выбери шрифт в таблице и впиши множитель или нужную высоту букв.',
        'status_working':   'Обработка… (у больших шрифтов это может занять несколько секунд)',
        'status_error':     'Ошибка.',
        'status_saved':     'Сохранено: {path}',
        'preview_was':      'было',
        'preview_will':     'будет ×%.3f',
        'preview_text':     'Привет, путник! Ты уверен?',
        'err_open_title':   'Не удалось открыть',
        'err_no_fonts_title': 'Нет шрифтов',
        'err_no_fonts':     'В файле нет шрифтов формата DefineFont3. Это не библиотека шрифтов Skyrim, либо формат не поддерживается.',
        'err_nothing_title': 'Нечего сохранять',
        'err_nothing':      'Все множители равны 1.0. Измени размер хотя бы у одного шрифта.',
        'dlg_save_title':   'Куда сохранить (имя файла лучше оставить прежним)',
        'dlg_open_title':   'Выбери SWF со шрифтами',
        'ft_swf':           'SWF',
        'ft_all':           'Все файлы',
        'done_title':       'Готово',
        'done_msg':         'Сохранено:\n%s\n\nИзменены: %s\n\nПоложи файл в мод по пути Interface\\%s с приоритетом выше оригинала.',
        'err_not_swf':      'Это не SWF-файл.',
        'err_lzma':         'SWF со сжатием LZMA (ZWS) не поддерживается.',
    },
}

_cur_lang = 'en'

def T(key):
    """Return localized string for the current language."""
    return LANG[_cur_lang].get(key, LANG['en'].get(key, key))

# ======================= low-level SWF routines =======================
class BR:
    def __init__(s, d, p=0): s.d = d; s.p = p; s.bit = 0; s.cur = 0
    def align(s): s.bit = 0
    def bits(s, n):
        v = 0
        for _ in range(n):
            if s.bit == 0: s.cur = s.d[s.p]; s.p += 1; s.bit = 8
            s.bit -= 1; v = (v << 1) | ((s.cur >> s.bit) & 1)
        return v
    def sbits(s, n):
        if n == 0: return 0
        v = s.bits(n)
        return v - (1 << n) if v & (1 << (n - 1)) else v

class BW:
    def __init__(s): s.out = bytearray(); s.cur = 0; s.n = 0
    def bits(s, v, n):
        for i in range(n - 1, -1, -1):
            s.cur = (s.cur << 1) | ((v >> i) & 1); s.n += 1
            if s.n == 8: s.out.append(s.cur); s.cur = 0; s.n = 0
    def sbits(s, v, n):
        if n == 0: return
        s.bits(v & ((1 << n) - 1), n)
    def align(s):
        if s.n: s.out.append((s.cur << (8 - s.n)) & 0xff); s.cur = 0; s.n = 0
    def bytes(s): s.align(); return bytes(s.out)

def need_s(v):
    return (v.bit_length() + 1) if v >= 0 else ((-v - 1).bit_length() + 1)

def parse_glyph(data, pos):
    br = BR(data, pos)
    nf = br.bits(4); nl = br.bits(4)
    recs = []; x = y = 0
    while True:
        if br.bits(1) == 0:
            fl = br.bits(5)
            if fl == 0: break
            if fl & 16: raise ValueError('new styles in glyph')
            r = {'t': 'S', 'mv': None, 'f0': None, 'f1': None, 'ln': None}
            if fl & 1:
                n = br.bits(5); x = br.sbits(n); y = br.sbits(n); r['mv'] = (x, y)
            if fl & 2: r['f0'] = br.bits(nf)
            if fl & 4: r['f1'] = br.bits(nf)
            if fl & 8: r['ln'] = br.bits(nl)
            recs.append(r)
        else:
            st = br.bits(1); n = br.bits(4) + 2
            if st:
                if br.bits(1): dx = br.sbits(n); dy = br.sbits(n)
                elif br.bits(1): dx = 0; dy = br.sbits(n)
                else: dx = br.sbits(n); dy = 0
                x += dx; y += dy; recs.append({'t': 'L', 'to': (x, y)})
            else:
                cx = x + br.sbits(n); cy = y + br.sbits(n)
                ax = cx + br.sbits(n); ay = cy + br.sbits(n)
                x, y = ax, ay; recs.append({'t': 'C', 'c': (cx, cy), 'to': (ax, ay)})
    return nf, nl, recs

def enc_glyph(nf, nl, recs, s):
    w = BW(); w.bits(nf, 4); w.bits(nl, 4)
    R = lambda v: int(round(v * s))
    x = y = 0
    for r in recs:
        if r['t'] == 'S':
            w.bits(0, 1)
            fl = (1 if r['mv'] else 0) | (2 if r['f0'] is not None else 0) | (4 if r['f1'] is not None else 0) | (8 if r['ln'] is not None else 0)
            w.bits(fl, 5)
            if r['mv']:
                nx, ny = R(r['mv'][0]), R(r['mv'][1])
                n = max(need_s(nx), need_s(ny)); w.bits(n, 5); w.sbits(nx, n); w.sbits(ny, n); x, y = nx, ny
            if r['f0'] is not None: w.bits(r['f0'], nf)
            if r['f1'] is not None: w.bits(r['f1'], nf)
            if r['ln'] is not None: w.bits(r['ln'], nl)
        elif r['t'] == 'L':
            nx, ny = R(r['to'][0]), R(r['to'][1]); dx, dy = nx - x, ny - y
            w.bits(1, 1); w.bits(1, 1)
            n = max(2, need_s(dx), need_s(dy)); w.bits(n - 2, 4)
            if dx and dy: w.bits(1, 1); w.sbits(dx, n); w.sbits(dy, n)
            elif dy: w.bits(0, 1); w.bits(1, 1); w.sbits(dy, n)
            else: w.bits(0, 1); w.bits(0, 1); w.sbits(dx, n)
            x, y = nx, ny
        else:
            cx, cy = R(r['c'][0]), R(r['c'][1]); ax, ay = R(r['to'][0]), R(r['to'][1])
            d = (cx - x, cy - y, ax - cx, ay - cy)
            w.bits(1, 1); w.bits(0, 1)
            n = max(2, *[need_s(v) for v in d]); w.bits(n - 2, 4)
            for v in d: w.sbits(v, n)
            x, y = ax, ay
    w.bits(0, 1); w.bits(0, 5)
    return w.bytes()

def read_rect(br):
    n = br.bits(5); v = [br.sbits(n) for _ in range(4)]; br.align(); return v

def write_rect(v):
    w = BW(); n = max(need_s(a) for a in v); w.bits(n, 5)
    for a in v: w.sbits(a, n)
    return w.bytes()

def load_swf(path):
    raw = open(path, 'rb').read()
    sig = raw[:3]
    if sig not in (b'FWS', b'CWS', b'ZWS'): raise ValueError(T('err_not_swf'))
    if sig == b'ZWS': raise ValueError(T('err_lzma'))
    body = raw[8:]
    if sig == b'CWS': body = zlib.decompress(body)
    br = BR(body); n = br.bits(5)
    for _ in range(4): br.sbits(n)
    br.align()
    return raw[3], body, br.p + 4

def iter_tags(body, p):
    while p + 2 <= len(body):
        hp = p
        h, = struct.unpack_from('<H', body, p); p += 2
        t = h >> 6; l = h & 0x3f
        if l == 0x3f: l, = struct.unpack_from('<I', body, p); p += 4
        yield t, hp, p, l
        p += l
        if t == 0: break

class FontInfo:
    """Parsed DefineFont3 (only what's needed for measurements and preview)."""
    def __init__(s, data):
        s.data = data
        fid, flags, lang, nlen = struct.unpack_from('<HBBB', data, 0); p = 5
        s.name = data[p:p + nlen].rstrip(b'\0').decode('utf8', 'replace'); p += nlen
        s.ng, = struct.unpack_from('<H', data, p); p += 2
        s.base = p
        wide = bool(flags & 8); osz = 4 if wide else 2; fmt = '<I' if wide else '<H'
        s.offs = [struct.unpack_from(fmt, data, s.base + osz * i)[0] for i in range(s.ng)]
        cto, = struct.unpack_from(fmt, data, s.base + osz * s.ng)
        ct = s.base + cto
        s.codes = list(struct.unpack_from('<%dH' % s.ng, data, ct))
        s.cmap = {c: i for i, c in enumerate(s.codes)}
        s.cyr = sum(1 for c in s.codes if 0x410 <= c <= 0x44f)
        s.adv = None
        if flags & 0x80:
            q = ct + 2 * s.ng + 6
            s.adv = list(struct.unpack_from('<%dh' % s.ng, data, q))
        s._gcache = {}
    def glyph(s, ch):
        i = s.cmap.get(ord(ch))
        if i is None: return None
        if i not in s._gcache:
            try: s._gcache[i] = parse_glyph(s.data, s.base + s.offs[i])
            except Exception: s._gcache[i] = None
        return s._gcache[i]
    def height(s, *chars):
        """Height of the first found glyph from chars, % of em."""
        for ch in chars:
            g = s.glyph(ch)
            if g is None: continue
            ys = []
            for r in g[2]:
                if r['t'] == 'S':
                    if r['mv']: ys.append(r['mv'][1])
                else: ys.append(r['to'][1])
            if ys: return (max(ys) - min(ys)) / EM * 100.0
        return None
    def contours(s, ch):
        """List of contours (polylines) in em units; curves split into segments."""
        g = s.glyph(ch)
        if g is None: return []
        res = []; cur = []; x = y = 0
        for r in g[2]:
            if r['t'] == 'S':
                if r['mv']:
                    if len(cur) > 1: res.append(cur)
                    x, y = r['mv']; cur = [(x, y)]
            elif r['t'] == 'L':
                x, y = r['to']; cur.append((x, y))
            else:
                (cx, cy), (ax, ay) = r['c'], r['to']
                for k in range(1, 7):
                    t = k / 6.0
                    cur.append(((1 - t) ** 2 * x + 2 * (1 - t) * t * cx + t * t * ax,
                                (1 - t) ** 2 * y + 2 * (1 - t) * t * cy + t * t * ay))
                x, y = ax, ay
        if len(cur) > 1: res.append(cur)
        return res

def list_fonts(path):
    ver, body, p = load_swf(path)
    fonts = []; other = 0
    for t, hp, dp, l in iter_tags(body, p):
        if t == 75:
            try: fonts.append(FontInfo(body[dp:dp + l]))
            except Exception: other += 1
        elif t == 48: other += 1
    return fonts, other

def scale_font3(d, s):
    fid, flags, lang, nlen = struct.unpack_from('<HBBB', d, 0); p = 5
    name = d[p:p + nlen]; p += nlen
    ng, = struct.unpack_from('<H', d, p); p += 2
    wide_off = bool(flags & 8); has_layout = bool(flags & 0x80)
    base = p; osz = 4 if wide_off else 2; fmt = '<I' if wide_off else '<H'
    offs = [struct.unpack_from(fmt, d, base + osz * i)[0] for i in range(ng)]
    cto, = struct.unpack_from(fmt, d, base + osz * ng)
    ct = base + cto
    codes = d[ct:ct + 2 * ng]; q = ct + 2 * ng
    blobs = [enc_glyph(nf, nl, recs, s) for nf, nl, recs in (parse_glyph(d, base + o) for o in offs)]
    cur = osz * ng + osz; new_offs = []
    for b in blobs: new_offs.append(cur); cur += len(b)
    out = bytearray(struct.pack('<HBBB', fid, flags, lang, nlen) + name + struct.pack('<H', ng))
    for o in new_offs: out += struct.pack(fmt, o)
    out += struct.pack(fmt, cur)
    for b in blobs: out += b
    out += codes
    if has_layout:
        asc, desc, lead = struct.unpack_from('<hhh', d, q); q += 6
        out += struct.pack('<hhh', int(round(asc * s)), int(round(desc * s)), int(round(lead * s)))
        for i in range(ng):
            a, = struct.unpack_from('<h', d, q); q += 2
            out += struct.pack('<h', int(round(a * s)))
        br = BR(d, q)
        for i in range(ng):
            xmin, xmax, ymin, ymax = read_rect(br)
            out += write_rect([math.floor(xmin * s), math.ceil(xmax * s), math.floor(ymin * s), math.ceil(ymax * s)])
        q = br.p
        kc, = struct.unpack_from('<H', d, q); q += 2
        max_kc = (len(d) - q) // 6
        kc = min(kc, max_kc)
        out += struct.pack('<H', kc)
        for i in range(kc):
            c1, c2, adj = struct.unpack_from('<HHh', d, q); q += 6
            out += struct.pack('<HHh', c1, c2, int(round(adj * s)))
    if q < len(d): out += d[q:]
    return bytes(out)

def save_scaled(src, dst, factors):
    """factors: {font_name: multiplier}; multiplier 1.0 is skipped."""
    ver, body, p = load_swf(src)
    br = BR(body); n = br.bits(5)
    for _ in range(4): br.sbits(n)
    br.align()
    hdr_end = br.p + 4
    out = bytearray(body[:hdr_end]); done = set()
    for t, hp, dp, l in iter_tags(body, hdr_end):
        data = body[dp:dp + l]
        if t == 75:
            nlen = data[4]; name = data[5:5 + nlen].rstrip(b'\0').decode('utf8', 'replace')
            f = factors.get(name, 1.0)
            if abs(f - 1.0) > 1e-9:
                new = scale_font3(data, f); done.add(name)
                out += struct.pack('<HI', (75 << 6) | 0x3f, len(new)) + new
                continue
        out += body[hp:dp + l]
    res = b'FWS' + bytes([ver]) + struct.pack('<I', len(out) + 8) + bytes(out)
    with open(dst, 'wb') as fh: fh.write(res)
    return done

# =============================== interface ===============================
def fnum(v, nd=1):
    return '—' if v is None else ('%.*f' % (nd, v))

def parse_float(s):
    return float(s.strip().replace(',', '.'))

class App:
    def __init__(self, root):
        self.root = root
        root.title('Skyrim Font Resizer')
        root.geometry('940x700'); root.minsize(860, 660)
        self.path = None; self.fonts = []; self.factor = {}
        self._build()
        if HAVE_DND:
            for w in (root, self.drop):
                w.drop_target_register(DND_FILES); w.dnd_bind('<<Drop>>', self._on_drop)

    def _build(self):
        r = self.root
        top = ttk.Frame(r, padding=8); top.pack(fill='x')
        self.drop = tk.Label(top, text=T('drop_dnd') if HAVE_DND else T('drop_no_dnd'),
                             relief='groove', bd=2, height=3, bg='#f0f0f0', font=('Segoe UI', 11))
        self.drop.pack(side='left', fill='x', expand=True)
        self.btn_open = ttk.Button(top, text=T('btn_open'), command=self.open_dialog)
        self.btn_open.pack(side='left', padx=(8, 0), ipadx=10, ipady=8)
        self.btn_lang = ttk.Button(top, text='RU', command=self._toggle_lang, width=4)
        self.btn_lang.pack(side='left', padx=(4, 0), ipady=8)
        self.fileinfo = ttk.Label(r, text=T('file_none'), padding=(10, 0)); self.fileinfo.pack(fill='x')

        cols = ('name', 'ng', 'cyr', 'cap', 'xh', 'k', 'ncap', 'nxh')
        widths = (230, 70, 90, 75, 75, 100, 110, 110)
        fr = ttk.Frame(r, padding=(8, 6)); fr.pack(fill='both', expand=True)
        self.tree = ttk.Treeview(fr, columns=cols, show='headings', height=6, selectmode='extended')
        self._col_keys = cols
        for c, w in zip(cols, widths):
            self.tree.heading(c, text=''); self.tree.column(c, width=w, anchor='w' if c == 'name' else 'center')
        sb = ttk.Scrollbar(fr, orient='vertical', command=self.tree.yview); self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side='left', fill='both', expand=True); sb.pack(side='left', fill='y')
        self.tree.bind('<<TreeviewSelect>>', self._on_select)

        self.frame_size = ttk.LabelFrame(r, text='', padding=8); self.frame_size.pack(fill='x', padx=8)
        self.e_k = tk.StringVar(); self.e_cap = tk.StringVar(); self.e_x = tk.StringVar()
        def entry(var, cmd, col):
            lbl = ttk.Label(self.frame_size, text='')
            lbl.grid(row=0, column=col * 2, sticky='e', padx=(0 if col == 0 else 14, 4))
            e = ttk.Entry(self.frame_size, textvariable=var, width=8); e.grid(row=0, column=col * 2 + 1)
            e.bind('<Return>', cmd); e.bind('<FocusOut>', cmd)
            return lbl
        self.lbl_k = entry(self.e_k, self._set_k, 0)
        self.lbl_cap = entry(self.e_cap, self._set_cap, 1)
        self.lbl_xh = entry(self.e_x, self._set_x, 2)
        self.btn_reset = ttk.Button(self.frame_size, text='', command=self.reset_all)
        self.btn_reset.grid(row=0, column=6, padx=(18, 0))
        self.lbl_hint = ttk.Label(self.frame_size, text='', foreground='#555')
        self.lbl_hint.grid(row=1, column=0, columnspan=7, sticky='w', pady=(6, 0))

        self.frame_preview = ttk.LabelFrame(r, text='', padding=4); self.frame_preview.pack(fill='x', padx=8, pady=6)
        self.canvas = tk.Canvas(self.frame_preview, height=130, bg='#1b1b1b', highlightthickness=0); self.canvas.pack(fill='x')

        bt = ttk.Frame(r, padding=(8, 0, 8, 8)); bt.pack(fill='x')
        self.btn_save = ttk.Button(bt, text=T('btn_save'), command=self.save, state='disabled')
        self.btn_save.pack(side='right', ipadx=14, ipady=4)
        self.status = ttk.Label(bt, text=T('status_ready')); self.status.pack(side='left')
        self.canvas.bind('<Configure>', lambda e: self._preview())

        self._retranslate()

    def _retranslate(self):
        """Update all UI text to match the current language."""
        self.drop.config(text=T('drop_dnd') if HAVE_DND else T('drop_no_dnd'))
        self.btn_open.config(text=T('btn_open'))
        self.btn_lang.config(text='RU' if _cur_lang == 'en' else 'EN')
        if not self.path:
            self.fileinfo.config(text=T('file_none'))

        col_map = {
            'name': 'col_name', 'ng': 'col_glyphs', 'cyr': 'col_cyr',
            'cap': 'col_cap', 'xh': 'col_xh', 'k': 'col_k',
            'ncap': 'col_ncap', 'nxh': 'col_nxh',
        }
        for c, key in col_map.items():
            self.tree.heading(c, text=T(key))

        self.frame_size.config(text=T('frame_size'))
        self.lbl_k.config(text=T('lbl_k'))
        self.lbl_cap.config(text=T('lbl_cap'))
        self.lbl_xh.config(text=T('lbl_xh'))
        self.btn_reset.config(text=T('btn_reset'))
        self.lbl_hint.config(text=T('vanilla_hint'))
        self.frame_preview.config(text=T('frame_preview'))
        self.btn_save.config(text=T('btn_save'))

        # refresh table rows (cyr yes/no) and file info
        if self.fonts:
            self._refresh_fileinfo()
            for i in range(len(self.fonts)):
                self._refresh_row(i)
        self._preview()

    def _toggle_lang(self):
        global _cur_lang
        _cur_lang = 'ru' if _cur_lang == 'en' else 'en'
        self._retranslate()

    def _refresh_fileinfo(self):
        if not self.path: return
        fonts, other = self.fonts, sum(1 for _ in [])  # other count not stored, use 0
        extra = ''
        self.fileinfo.config(text=T('file_info').format(
            name=os.path.basename(self.path), n=len(self.fonts), extra=extra))

    # ---- opening a file ----
    def _on_drop(self, ev):
        items = self.root.tk.splitlist(ev.data)
        if items: self.load(items[0])
    def open_dialog(self):
        p = filedialog.askopenfilename(title=T('dlg_open_title'),
                                       filetypes=[(T('ft_swf'), '*.swf'), (T('ft_all'), '*.*')])
        if p: self.load(p)
    def load(self, path):
        try:
            fonts, other = list_fonts(path)
        except Exception as ex:
            messagebox.showerror(T('err_open_title'), str(ex)); return
        if not fonts:
            messagebox.showwarning(T('err_no_fonts_title'), T('err_no_fonts')); return
        self.path = path; self.fonts = fonts; self.factor = {f.name: 1.0 for f in fonts}
        self._other_count = other
        extra = T('file_extra').format(n=other) if other else ''
        self.fileinfo.config(text=T('file_info').format(
            name=os.path.basename(path), n=len(fonts), extra=extra))
        self.tree.delete(*self.tree.get_children())
        self.meas = {}
        for i, f in enumerate(fonts):
            cap = f.height('Н', 'H'); xh = f.height('х', 'x')
            self.meas[i] = (cap, xh)
            self.tree.insert('', 'end', iid=str(i), values=(
                f.name, f.ng, T('cyr_yes') if f.cyr else T('cyr_no'),
                fnum(cap), fnum(xh), '1.000', fnum(cap), fnum(xh)))
        self.btn_save.config(state='normal'); self.status.config(text=T('status_select'))
        self.tree.selection_set('0'); self._on_select()

    # ---- editing size ----
    def _sel(self): return [int(i) for i in self.tree.selection()]
    def _refresh_row(self, i):
        f = self.fonts[i]; k = self.factor[f.name]; cap, xh = self.meas[i]
        self.tree.item(str(i), values=(
            f.name, f.ng, T('cyr_yes') if f.cyr else T('cyr_no'),
            fnum(cap), fnum(xh), '%.3f' % k,
            fnum(cap * k if cap else None), fnum(xh * k if xh else None)))
    def _apply(self, i, k):
        k = max(0.2, min(5.0, k)); self.factor[self.fonts[i].name] = k; self._refresh_row(i)
    def _set_k(self, ev=None):
        sel = self._sel()
        if not sel: return
        try: k = parse_float(self.e_k.get())
        except Exception: self._on_select(); return
        for i in sel: self._apply(i, k)
        self._on_select(keep=True)
    def _set_target(self, var, idx):
        sel = self._sel()
        if not sel: return
        try: t = parse_float(var.get())
        except Exception: self._on_select(); return
        for i in sel:
            base = self.meas[i][idx]
            if base: self._apply(i, t / base)
        self._on_select(keep=True)
    def _set_cap(self, ev=None): self._set_target(self.e_cap, 0)
    def _set_x(self, ev=None): self._set_target(self.e_x, 1)
    def _on_select(self, ev=None, keep=False):
        sel = self._sel()
        if sel:
            i = sel[0]; k = self.factor[self.fonts[i].name]; cap, xh = self.meas[i]
            self.e_k.set('%.3f' % k)
            self.e_cap.set(fnum(cap * k) if cap else ''); self.e_x.set(fnum(xh * k) if xh else '')
        self._preview()
    def reset_all(self):
        for i, f in enumerate(self.fonts): self.factor[f.name] = 1.0; self._refresh_row(i)
        self._on_select()

    # ---- preview ----
    def _draw_line(self, f, text, k, y_base, px):
        sc = px / EM; x = 14; c = self.canvas
        for ch in text:
            if ch == ' ':
                i = f.cmap.get(32); adv = (f.adv[i] if (f.adv and i is not None) else 4000)
                x += adv * sc * k; continue
            for cont in f.contours(ch):
                pts = []
                for (gx, gy) in cont: pts += [x + gx * sc * k, y_base + gy * sc * k]
                c.create_line(*pts, fill='#e8e8e8', width=1)
            i = f.cmap.get(ord(ch)); adv = (f.adv[i] if (f.adv and i is not None) else 9000)
            x += adv * sc * k
    def _preview(self):
        c = self.canvas; c.delete('all')
        sel = self._sel()
        if not sel: return
        f = self.fonts[sel[0]]; k = self.factor[f.name]
        text = 'Hello, traveler! Are you sure?'
        if f.cyr:
            text = LANG['ru'].get('preview_text', text) if _cur_lang == 'ru' else text
        px = 40
        self._draw_line(f, text, 1.0, 50, px)
        c.create_line(0, 66, 4000, 66, fill='#444', dash=(2, 3))
        self._draw_line(f, text, k, 118, px)
        c.create_text(c.winfo_width() - 8, 8, text=T('preview_was'), fill='#7a7', anchor='ne')
        c.create_text(c.winfo_width() - 8, 72, text=T('preview_will') % k, fill='#7a7', anchor='ne')

    # ---- saving ----
    def save(self):
        changed = {n: k for n, k in self.factor.items() if abs(k - 1.0) > 1e-9}
        if not changed:
            messagebox.showinfo(T('err_nothing_title'), T('err_nothing')); return
        base = os.path.basename(self.path)
        dst = filedialog.asksaveasfilename(title=T('dlg_save_title'), initialdir=os.path.dirname(self.path),
                                           initialfile=base, defaultextension='.swf',
                                           filetypes=[(T('ft_swf'), '*.swf')])
        if not dst: return

        self.btn_save.config(state='disabled'); self.status.config(text=T('status_working'))
        def work():
            try: save_scaled(self.path, dst, changed); err = None
            except Exception: err = traceback.format_exc()
            self.root.after(0, lambda: self._done(dst, err, changed))
        threading.Thread(target=work, daemon=True).start()
    def _done(self, dst, err, changed):
        self.btn_save.config(state='normal')
        if err:
            self.status.config(text=T('status_error')); messagebox.showerror(T('status_error'), err); return
        self.status.config(text=T('status_saved').format(path=dst))
        messagebox.showinfo(T('done_title'), T('done_msg') % (
            dst, ', '.join('%s ×%.3f' % kv for kv in changed.items()), os.path.basename(dst)))

def main():
    try:
        import ctypes; ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception: pass
    root = TkinterDnD.Tk() if HAVE_DND else tk.Tk()
    app = App(root)
    if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):   # SWF dropped on exe or passed as argument
        root.after(150, lambda: app.load(sys.argv[1]))
    root.mainloop()

if __name__ == '__main__':
    main()
