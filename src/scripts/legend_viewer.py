import streamlit as st
from typing import List, Dict, Any
from pathlib import Path
import json
import csv
import base64
import streamlit.components.v1 as components
from pathlib import Path as _Path_for_encode  # avoid shadowing existing Path usage

# enable wide layout so table can fill more page width (safe-guard if called multiple times)
try:
	st.set_page_config(layout="wide")
except Exception:
	# already set or called too late; ignore
	pass

def _placeholder_img(text: str, size: int = 64) -> str:
	# simple placeholder image with text; safe and copyright-free
	return f"https://via.placeholder.com/{size}?text={text.replace(' ', '+')}"

# project base (two levels up from this script: meet_legends)
_BASE_DIR = Path(__file__).resolve().parents[2]
_RESOURCES_DIR = _BASE_DIR / "resources"
_CONFIG_MAP_PATH = _BASE_DIR / "src" / "config" / "name_to_filename.json"
_DATA_CSV_PATH = _BASE_DIR / "data" / "data.csv"

# Added debug prints so you can see what paths are being used
print(f"[legend_viewer] BASE_DIR: {_BASE_DIR}")
print(f"[legend_viewer] RESOURCES_DIR: {_RESOURCES_DIR}")
print(f"[legend_viewer] CONFIG_MAP_PATH: {_CONFIG_MAP_PATH} (exists={_CONFIG_MAP_PATH.exists()})")
print(f"[legend_viewer] DATA_CSV_PATH: {_DATA_CSV_PATH} (exists={_DATA_CSV_PATH.exists()})")

def _load_name_map() -> Dict[str, str]:
	"""Load name -> filename mapping from config JSON."""
	print(f"[legend_viewer] Attempting to load name map from {_CONFIG_MAP_PATH}")
	if not _CONFIG_MAP_PATH.exists():
		print("[legend_viewer] name map file not found.")
		return {}
	try:
		with open(_CONFIG_MAP_PATH, "r", encoding="utf-8") as fh:
			data = json.load(fh)
			print(f"[legend_viewer] Loaded name map entries: {len(data)}")
			return data
	except Exception as e:
		print(f"[legend_viewer] Failed to load name map: {e}")
		return {}

def _load_data_csv() -> Dict[str, Dict[str, Any]]:
	"""Load data.csv into a mapping: legend_name -> {weapons: [...], stats: {...}}."""
	print(f"[legend_viewer] Attempting to load data CSV from {_DATA_CSV_PATH}")
	result: Dict[str, Dict[str, Any]] = {}
	if not _DATA_CSV_PATH.exists():
		print("[legend_viewer] data.csv not found.")
		return result
	try:
		with open(_DATA_CSV_PATH, newline="", encoding="utf-8") as csvfile:
			reader = csv.DictReader(csvfile)
			print(f"[legend_viewer] CSV fieldnames: {reader.fieldnames}")
			for row in reader:
				legend = (row.get("Legend") or "").strip()
				if not legend:
					continue
				weapons = []
				w1 = (row.get("Weapon 1") or "").strip()
				w2 = (row.get("Weapon 2") or "").strip()
				if w1:
					weapons.append(w1)
				if w2:
					weapons.append(w2)
				# stats columns as provided
				stats = {
					"Strength": (row.get("Strength") or "").strip(),
					"Dexterity": (row.get("Dexterity") or "").strip(),
					"Defense": (row.get("Defense") or "").strip(),
					"Speed": (row.get("Speed") or "").strip(),
				}
				result[legend] = {"weapons": weapons, "stats": stats}
	except Exception as e:
		print(f"[legend_viewer] Failed to read data.csv: {e}")
		return {}
	print(f"[legend_viewer] Loaded data for {len(result)} legends from CSV")
	return result

_name_map = _load_name_map()
_data_bank = _load_data_csv()

def _resolve_resource_path(kind: str, name: str) -> str:
	"""
	Resolve the resource filepath for a given kind ("legends" or "weapons")
	using the _name_map. If file missing or no mapping, try constructed filenames
	(lowercase, spaces -> underscores) with .png/.jpg and finally scan folder by stem.
	"""
	print(f"[legend_viewer] Resolving {kind} resource for '{name}'")
	res_dir = _RESOURCES_DIR / kind

	candidates = []
	# first, try mapping from config if present
	mapped = _name_map.get(name)
	if mapped:
		candidates.append(mapped)
		# if mapping missing extension, also try common extensions
		if not Path(mapped).suffix:
			candidates.append(f"{mapped}.png")
			candidates.append(f"{mapped}.jpg")

	# next, construct canonical filenames from the name
	stem = name.strip().lower().replace(" ", "_")
	candidates.append(f"{stem}.png")
	candidates.append(f"{stem}.jpg")
	candidates.append(stem)  # in case mapping uses no extension or custom handling

	# try each candidate
	for cand in candidates:
		full_path = res_dir / cand
		print(f"[legend_viewer] Trying candidate filename: {cand} -> {full_path} (exists={full_path.exists()})")
		if full_path.exists():
			print(f"[legend_viewer] Found local file: {full_path}")
			return str(full_path)

	# last resort: case-insensitive stem match by scanning the directory
	try:
		if res_dir.exists():
			for p in res_dir.iterdir():
				if not p.is_file():
					continue
				p_stem = p.stem.lower()
				if p_stem == stem:
					print(f"[legend_viewer] Found by stem scan: {p}")
					return str(p)
	except Exception as e:
		print(f"[legend_viewer] Error scanning resource dir {res_dir}: {e}")

	# fallback to placeholder if nothing matches
	url = _placeholder_img(name, 96 if kind == "legends" else 48)
	print(f"[legend_viewer] No local file found for '{name}'; using placeholder {url}")
	return url

def _stat_abbrev(stat_name: str) -> str:
	abbr = {
		"Strength": "STR",
		"Dexterity": "DEX",
		"Defense": "DEF",
		"Speed": "SPD",
	}
	return abbr.get(stat_name, stat_name[:3].upper())

def _resolve_stat_image(stat_name: str) -> str:
	"""
	Resolve the image path for a stat from resources/stats.
	Uses lowercase, underscores, .png/.jpg.
	"""
	res_dir = _RESOURCES_DIR / "stats"
	stem = stat_name.strip().lower().replace(" ", "_")
	candidates = [f"{stem}.png", f"{stem}.jpg", stem]
	for cand in candidates:
		full_path = res_dir / cand
		if full_path.exists():
			return str(full_path)
	# fallback to placeholder if not found
	return _placeholder_img(stat_name, 32)

def _get_legend_data(name: str) -> Dict:
	# try data from CSV first
	key = name.strip()
	entry = _data_bank.get(key)
	# base output
	out = {"image": None, "weapons": [], "stats": []}
	# resolve legend portrait from resources/legends via name map
	out["image"] = _resolve_resource_path("legends", key)
	# weapons: from CSV if available, otherwise fallback to name_map or placeholders
	if entry:
		for wname in entry.get("weapons", []):
			img = _resolve_resource_path("weapons", wname)
			out["weapons"].append({"name": wname, "image": img})
		# stats: use values from CSV, images from resources/stats
		for stat_name in ["Strength", "Dexterity", "Defense", "Speed"]:
			val = entry.get("stats", {}).get(stat_name, "")
			# Ensure stat is displayed as integer if possible
			if val != "":
				try:
					val_int = int(float(val))
					label = str(val_int)
				except Exception:
					label = str(val)
			else:
				label = "—"
			out["stats"].append({
				"stat": stat_name,
				"name": label,
				"image": _resolve_stat_image(stat_name)
			})
	else:
		# fallback: try to find two weapons by attempting common keys in name_map
		# (this keeps behavior resilient if CSV missing)
		# assemble any weapon names from name_map that look related (not reliable)
		# simply provide two placeholder weapons
		out["weapons"] = [
			{"name": "Weapon A", "image": _placeholder_img("WpnA", 48)},
			{"name": "Weapon B", "image": _placeholder_img("WpnB", 48)},
		]
		# fallback stats: only placeholder values (no labels)
		out["stats"] = [
			{"stat": "Strength", "name": "—", "image": _resolve_stat_image("Strength")},
			{"stat": "Dexterity", "name": "—", "image": _resolve_stat_image("Dexterity")},
			{"stat": "Defense", "name": "—", "image": _resolve_stat_image("Defense")},
			{"stat": "Speed", "name": "—", "image": _resolve_stat_image("Speed")},
		]
	return out

def _img_src_for_html(path: str) -> str:
	"""
	Return a source suitable for an <img src="..."> tag:
	- if path is a URL, return it
	- if path is local, encode as data URI (png/jpg)
	- otherwise return placeholder URL
	"""
	if not path:
		return _placeholder_img("missing", 64)
	if isinstance(path, str) and (path.startswith("http://") or path.startswith("https://")):
		return path
	try:
		p = _Path_for_encode(path)
		if p.exists() and p.is_file():
			ext = p.suffix.lower().lstrip(".")
			mime = "image/png" if ext == "png" or ext == "" else f"image/{ext}"
			data = p.read_bytes()
			b64 = base64.b64encode(data).decode("ascii")
			return f"data:{mime};base64,{b64}"
	# fall back to placeholder and catch errors
	except Exception as e:
		print(f"[legend_viewer] _img_src_for_html error for {path}: {e}")
	return _placeholder_img("missing", 64)

def display_legends(legends: List[str]):
	"""
	Render legends as a single HTML table (gridlines + styled headers + larger name).
	"""
	if not legends:
		st.write("No legends found.")
		return

	# Build HTML table
	css = """
 	<style>
 	:root{
 		--th-bg: #ffffff;              /* keep headers bright in light mode */
 		--td-bg: #ffffff;
 		--header-color: #0b3d91;
 		--text-color: #000000;         /* absolute black for strong contrast in light mode */
 		--border: #aeb9c4;             /* slightly stronger border */
 		--caption-bg: #ffffff;         /* solid white caption background for max contrast */
 		--caption-text: #031128;       /* deep navy caption text */
 		--row-bg: transparent;
 	}
 	@media (prefers-color-scheme: dark) {
 		:root{
 			--th-bg: #071033;              /* header surface in dark mode */
 			--td-bg: rgba(255,255,255,0.02); /* cell surface */
 			--header-color: #9ec5ff;       /* lighter blue for headers */
 			--text-color: #e6f2ff;         /* primary text in dark */
 			--border: rgba(255,255,255,0.06);
 			--caption-bg: rgba(255,255,255,0.03);
 			--caption-text: #e6eef8;
 			--row-bg: transparent;
 		}
 	}

 	.lv-table { width: 100%; border-collapse: collapse; font-family: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial; }
 	.lv-table th { background: var(--th-bg); padding: 10px; border: 1px solid var(--border); text-align: left; font-weight: 800; color: var(--header-color); font-size: 18px; }
 	/* stronger, higher-contrast body text in cells for light mode */
 	.lv-table td { padding: 12px; border: 1px solid var(--border); vertical-align: top; background: var(--td-bg); color: var(--text-color); font-size: 15px; font-weight: 900; }
 	.lv-portrait img { width: 120px; height: auto; border-radius: 6px; display:block; }
 	.lv-name { font-size: 26px; font-weight: 900; margin: 4px 0; color: var(--header-color); }
 	.lv-weapons { display: flex; gap: 12px; flex-wrap: wrap; align-items: flex-start; }
 	/* stats rendered in a 2x2 grid: Strength (top-left), Defense (top-right), Dexterity (bottom-left), Speed (bottom-right) */
 	.lv-stats-grid {
 		display: grid;
 		grid-template-columns: 1fr 1fr;
 		grid-template-rows: auto auto;
 		grid-template-areas:
 			"str def"
 			"dex spd";
 		gap: 12px;
 		align-items: start;
 	}
 	.lv-weapon, .lv-stat { text-align: center; max-width: 160px; min-width: 80px; }
 	.lv-stat.str { grid-area: str; }
 	.lv-stat.def { grid-area: def; }
 	.lv-stat.dex { grid-area: dex; }
 	.lv-stat.spd { grid-area: spd; }
 	.lv-weapon img { width: 56px; height: auto; display:block; margin: 0 auto 6px; border-radius:4px; }
 	.lv-stat img { width: 40px; height: auto; display:block; margin: 0 auto 6px; border-radius:4px; }
 	/* very legible, high-contrast captions in light mode while preserving dark mode settings */
 	.lv-caption {
 		font-size: 15px;
 		color: var(--caption-text);
 		font-weight: 900;
 		background: var(--caption-bg);
 		padding: 6px 10px;
 		border-radius: 8px;
 		border: 1px solid rgba(2,20,45,0.08);
 		word-break: break-word;
 		display: inline-block;
 	}
 	/* subtle row hover for readability */
 	.lv-table tbody tr:hover td { background: rgba(0,0,0,0.04); }
 	@media (prefers-color-scheme: dark) {
 		.lv-table tbody tr:hover td { background: rgba(255,255,255,0.02); }
 	}
 	</style>
 	"""

	# header row
	html_rows = []
	html_rows.append("<table class='lv-table'>")
	html_rows.append("<thead><tr>")
	html_rows.append("<th style='width:140px;'></th>")  # portrait column - unlabeled
	# narrower weapons column, larger name column; stats gets remaining width
	html_rows.append("<th style='width:25%;'>Name</th>")
	html_rows.append("<th style='width:30%;'>Weapons</th>")
	html_rows.append("<th style='width:45%;'>Stats</th>")
	html_rows.append("</tr></thead>")
	html_rows.append("<tbody>")

	for name in legends:
		data = _get_legend_data(name)
		# portrait image source suitable for HTML
		portrait_src = _img_src_for_html(data.get("image"))
		# weapons HTML
		weapons_html = ""
		for w in data.get("weapons", []):
			w_src = _img_src_for_html(w.get("image"))
			w_name = w.get("name") or ""
			weapons_html += (
				f"<div class='lv-weapon'><img src='{w_src}' alt='{w_name}' /><div class='lv-caption'>{w_name}</div></div>"
			)
		if not weapons_html:
			weapons_html = "<div class='lv-caption'>—</div>"

		# stats HTML
		# build mapping from stat key -> entry for robust placement
		stats_map = { (s.get("stat") or "").strip(): s for s in data.get("stats", []) }
		# ensure each stat exists, fallback to placeholder
		def stat_entry(key):
			if key in stats_map:
				return stats_map[key]
			# fallback placeholder
			return {"stat": key, "name": "—", "image": _placeholder_img(_stat_abbrev(key), 32)}

		s_str = stat_entry("Strength")
		s_def = stat_entry("Defense")
		s_dex = stat_entry("Dexterity")
		s_spd = stat_entry("Speed")

		stats_html = (
			"<div class='lv-stats-grid'>"
			f"<div class='lv-stat str'><img src='{_img_src_for_html(s_str.get('image'))}' alt='Strength' /><div class='lv-caption'>{s_str.get('name')}</div></div>"
			f"<div class='lv-stat def'><img src='{_img_src_for_html(s_def.get('image'))}' alt='Defense' /><div class='lv-caption'>{s_def.get('name')}</div></div>"
			f"<div class='lv-stat dex'><img src='{_img_src_for_html(s_dex.get('image'))}' alt='Dexterity' /><div class='lv-caption'>{s_dex.get('name')}</div></div>"
			f"<div class='lv-stat spd'><img src='{_img_src_for_html(s_spd.get('image'))}' alt='Speed' /><div class='lv-caption'>{s_spd.get('name')}</div></div>"
			"</div>"
		)

		# assemble row
		row = (
			"<tr>"
			f"<td class='lv-portrait'><img src='{portrait_src}' alt='{name}'/></td>"
			f"<td><div class='lv-name'>{name}</div></td>"
			f"<td><div class='lv-weapons'>{weapons_html}</div></td>"
			f"<td>{stats_html}</td>"
			"</tr>"
		)
		html_rows.append(row)

	html_rows.append("</tbody></table>")

	html = css + "".join(html_rows)

	# compute a reasonable height for the component
	height = max(400, 160 * len(legends))
	components.html(html, height=height, scrolling=True)
