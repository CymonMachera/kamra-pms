"""Seed Citizen Lodge (Mwanza, Tanzania) for evaluation.

Run via:
    bench --site kamra.localhost execute kamra.scripts.seed_citizen_lodge.execute

Idempotent. Mirrors the real lodge: 10 named rooms, TZS rates, Tembo as the
only twin (4 guests), everything else a double.
"""

import frappe

PROPERTY = "Citizen Lodge"

# (code, name, price TZS, max_guests)
ROOMS = [
	("KIB", "Kiboko", 25000, 2),
	("TEM", "Tembo", 30000, 4),
	("KIF", "Kifaru", 20000, 2),
	("TAU", "Tausi", 20000, 2),
	("SUN", "Sungura", 25000, 2),
	("SIM", "Simba", 20000, 2),
	("NYA", "Nyati", 25000, 2),
	("CHU", "Chui", 20000, 2),
	("SWA", "Swala", 20000, 2),
	("TWI", "Twiga", 20000, 2),
]


def _set_if_has(doc, **kwargs):
	"""Set only fields this Frappe/Kamra version actually defines."""
	for key, value in kwargs.items():
		if doc.meta.has_field(key):
			doc.set(key, value)


def ensure_property():
	if frappe.db.exists("Property", PROPERTY):
		print(f"property exists: {PROPERTY}")
		return PROPERTY
	doc = frappe.new_doc("Property")
	doc.property_name = PROPERTY
	_set_if_has(
		doc,
		currency="TZS",
		country="Tanzania",
		city="Mwanza",
		address_line1="Citizen Lodge, Mwanza",
		timezone="Africa/Dar_es_Salaam",
		check_in_time="12:00:00",
		check_out_time="10:00:00",
		email="cymonmachera1@gmail.com",
		phone="+255 000 000 000",
	)
	doc.flags.ignore_mandatory = True
	doc.insert(ignore_permissions=True)
	print(f"created property: {PROPERTY}")
	return doc.name


def ensure_rooms(prop):
	for code, name, price, guests in ROOMS:
		rt_name = f"{prop}-{code}"
		if not frappe.db.exists("Room Type", rt_name):
			rt = frappe.new_doc("Room Type")
			rt.property = prop
			rt.room_type_code = code
			rt.room_type_name = name
			rt.base_price = price
			_set_if_has(rt, max_occupancy=guests, max_adults=guests, base_occupancy=2)
			rt.flags.ignore_mandatory = True
			rt.insert(ignore_permissions=True)
			print(f"  room type: {name} @ TZS {price:,}")

		room_name = f"{prop}-{name}"
		if not frappe.db.exists("Room", room_name):
			room = frappe.new_doc("Room")
			room.property = prop
			room.room_number = name          # guests know rooms by name here
			room.room_type = rt_name
			_set_if_has(room, floor="Ground", status="Available", housekeeping_status="Clean")
			room.flags.ignore_mandatory = True
			room.insert(ignore_permissions=True)
			print(f"  room: {name}")


def execute():
	prop = ensure_property()
	ensure_rooms(prop)
	frappe.db.commit()
	print(
		f"\nCitizen Lodge ready: "
		f"{frappe.db.count('Room Type', {'property': prop})} room types, "
		f"{frappe.db.count('Room', {'property': prop})} rooms."
	)
