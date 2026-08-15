# Regulatory Scope & Limitations

This platform provides **decision support and coordination tooling** for a coastal
port/harbor authority. It is **not**:

- A certified navigation, ARPA, or safety-of-life radar/collision-avoidance system
- A substitute for a Master's or pilot's professional judgment or COLREGS obligations
- A certified fatigue-management system for pilotage rest-hour compliance
- A direct filing integration with any specific national single-window customs/
  immigration system (US CBP eNOA/D, EU PortNet, etc.) — the `customs_integration`
  service checks timing and completeness of manifest data already provided to it
- A definitive interpretation of IMO conventions — the `imo_compliance` checklist is an
  operational aid reflecting commonly-tracked FAL/BWM/MARPOL documentation items, not a
  legal compliance determination

## What it does provide

- CPA/TCPA collision **risk screening** as a situational-awareness aid, using the same
  underlying technique (not certification) as commercial ARPA systems
- A configurable harmonic tidal model for under-keel clearance estimation — **must be
  calibrated with your station's official harmonic constituent table** before
  operational use (see `app/services/tidal_calculations.py`)
- A rule-based pilot rest-hour threshold as a starting point — replace with your
  pilotage authority's certified policy
- A structured checklist mirroring common IMO FAL Convention, BWM Convention, and
  MARPOL Annex documentation requirements, to help operations staff track what's
  outstanding before berth assignment

## Before operational use

Any deployment of this system for real port operations should be reviewed by your
harbor master's office, legal/compliance team, and (where applicable) flag-state or
port-state control authority, and calibrated with your jurisdiction's actual
regulatory requirements, tidal data, and pilotage rules.
