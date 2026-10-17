"""
medical_image_labeler.py
=========================
Continuous Internal Assessment (CIA Tool) - Group F: Technology Enabled Assessment
F3: Coding Assignment — Virtual & Augmented Reality (V&AR)
Course Code : CSDO7012
Course Name : AI for Healthcare (BE Sem VII)
Module - VI : Future of Healthcare using AI
Group       : Group 6

APPLICATION TITLE:
"BioVision 3D — Holographic AR/VR Medical Anatomy & Clinical Pathology Visualizer"

PROJECT DESCRIPTION & BLOOM'S LEVEL (APPLY):
This application implements an interactive 3D Virtual & Augmented Reality (V&AR)
medical visualizer designed for clinical diagnosis, junior doctor training, and
AR-assisted surgical planning.

KEY CAPABILITIES:
1. True 3D Parametric Human Anatomy Engine:
   - Full 3D anatomical geometry (not a stickman): contoured skull, curved spine,
     ribcage arches, pelvis, long bones, cardiovascular arterial/venous trees,
     muscle envelopes, and visceral organ volumes.
2. 4 Overlapping Anatomical Layers (Multi-layer Stacking & Blending):
   - 🦴 SKELETAL SYSTEM   : Cranium, vertebrae, 10 paired rib arches, pelvis, limbs.
   - 🫀 CIRCULATORY SYSTEM: Heart chamber, aorta, vena cava, carotids, femoral network.
   - 💪 MUSCULAR SYSTEM   : Pectorals, deltoids, biceps, rectus abdominis, quadriceps.
   - 🧠 VISCERAL SYSTEM   : Lungs, liver, stomach, kidneys, brain cerebrum.
   * Individual visibility toggles and opacity controls allow simultaneous layer blending.
3. Clinical Pathology & Diagnostic Issues (NOT body parts):
   - Anchored in real 3D anatomical space with ICD-10 clinical diagnostic data.
   - Color-coded severity triage: CRITICAL (Red), HIGH (Orange), MODERATE (Yellow).
   - Clinical issues: Myocardial Infarction, Femur Fracture, Aortic Aneurysm,
     Tension Pneumothorax, Lumbar Disc Herniation, Biceps Tendon Rupture, etc.
   - Interactive diagnostic HUD card with surgical planning guidance.
   - Ability to add custom clinical issues at any 3D coordinate.
4. Dual Reality Modes (Virtual Reality + Augmented Reality):
   - 📡 AR HOLOGRAPHIC HUD MODE: Single-viewport sci-fi medical HUD with 3D ground
     grid, telemetry readouts, floating billboarding issue pins, and targeting reticle.
   - 🥽 VR STEREOSCOPIC 3D MODE: Dual side-by-side viewport (Left Eye / Right Eye)
     with genuine binocular parallax (IPD optical separation) and simulated VR
     headset lens barrel vignettes (Oculus Quest / Apple Vision Pro simulation).
5. 360° Real-time 3D Navigation:
   - Left-Click Drag: 360° Orbit (Yaw & Pitch)
   - Right-Click Drag: Pan (X, Y)
   - Scroll Wheel: Zoom in/out
   - Auto-Orbit: Automated 3D holographic turntable showcase
   - Camera Presets: Anterior, Posterior, Lateral, Thorax Close-up, Cranial Close-up.
"""

import json
import math
import os
import sys
import time
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Any, Optional

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageTk

# ─────────────────────────────────────────────────────────────────────────────
# 1. THEME CONSTANTS & COLOR PALETTE
# ─────────────────────────────────────────────────────────────────────────────
BG_COLOR = "#080c14"
CANVAS_BG = "#04070d"
PANEL_BG = "#0d1424"
PANEL_ALT_BG = "#131d33"
ACCENT_CYAN = "#00f0ff"
ACCENT_GREEN = "#00ff9d"
ACCENT_YELLOW = "#facc15"
ACCENT_ORANGE = "#fb923c"
ACCENT_RED = "#f43f5e"
TEXT_PRIMARY = "#f8fafc"
TEXT_MUTED = "#94a3b8"
BORDER_COLOR = "#1e293b"

# Layer Color Definitions
COLOR_SKELETAL = "#cbd5e1"      # Ivory Bone Slate
COLOR_CIRC_ART = "#ff3b5c"      # Arterial Crimson
COLOR_CIRC_VEN = "#38bdf8"      # Venous Azure
COLOR_MUSCULAR = "#fb7185"      # Muscle Coral
COLOR_VISCERAL = "#34d399"      # Visceral Emerald
COLOR_GRID = "#0f2038"          # 3D Holographic Grid

# ─────────────────────────────────────────────────────────────────────────────
# 2. CLINICAL PATHOLOGY DATA MODEL
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class ClinicalIssue:
    """Represents a diagnosed medical pathology attached to 3D anatomical space."""
    id: str
    name: str
    system: str              # Skeletal, Circulatory, Muscular, Visceral
    severity: str            # CRITICAL, HIGH, MODERATE
    coord_3d: np.ndarray     # (x, y, z) 3D coordinate
    icd10: str
    symptoms: str
    intervention: str

    @property
    def severity_color(self) -> str:
        if self.severity == "CRITICAL":
            return ACCENT_RED
        elif self.severity == "HIGH":
            return ACCENT_ORANGE
        return ACCENT_YELLOW


# ─────────────────────────────────────────────────────────────────────────────
# 3. 3D ANATOMICAL GEOMETRY BUILDER (NO STICKMAN — MULTI-LAYERED)
# ─────────────────────────────────────────────────────────────────────────────
class Anatomy3DEngine:
    """
    Constructs high-fidelity 3D parametric curves, contours, and volumetric
    structures for Skeletal, Circulatory, Muscular, and Visceral systems.
    Coordinates: X in [-1.5, 1.5] (lateral), Y in [-3.0, 3.0] (vertical), Z in [-1.0, 1.0] (depth).
    """

    @staticmethod
    def _circle_3d(cx: float, cy: float, cz: float, rx: float, ry: float, rz: float = 0.0,
                   n: int = 24, plane: str = "xy") -> np.ndarray:
        """Helper to generate 3D elliptical wireframe rings."""
        t = np.linspace(0, 2 * np.pi, n)
        if plane == "xy":
            x = cx + rx * np.cos(t)
            y = cy + ry * np.sin(t)
            z = np.full_like(t, cz)
        elif plane == "xz":
            x = cx + rx * np.cos(t)
            y = np.full_like(t, cy)
            z = cz + rz * np.sin(t)
        elif plane == "yz":
            x = np.full_like(t, cx)
            y = cy + ry * np.cos(t)
            z = cz + rz * np.sin(t)
        else:
            x, y, z = np.zeros_like(t), np.zeros_like(t), np.zeros_like(t)
        return np.column_stack([x, y, z])

    @staticmethod
    def _line_3d(p1: Tuple[float, float, float], p2: Tuple[float, float, float],
                 n: int = 10) -> np.ndarray:
        """Helper to generate smooth 3D line segments."""
        return np.linspace(p1, p2, n)

    @classmethod
    def build_skeletal_layer(cls) -> List[Dict[str, Any]]:
        """Constructs 3D Cranium, Spine, 10 paired Ribs, Clavicles, Pelvis, and Limbs."""
        elements = []

        # ── 1. Cranium / Skull Vault ──
        # Latitudinal cranial rings
        for y_deg, r_scale in [(2.45, 0.32), (2.65, 0.40), (2.85, 0.42), (3.0, 0.36), (3.12, 0.22)]:
            pts = cls._circle_3d(0.0, y_deg, 0.05, rx=r_scale * 0.9, ry=0, rz=r_scale * 1.05, n=24, plane="xz")
            elements.append({"type": "loop", "pts": pts, "color": COLOR_SKELETAL, "width": 1})

        # Longitudinal sagittal & coronal arches
        t = np.linspace(0, np.pi, 25)
        # Sagittal crest
        sagittal = np.column_stack([np.zeros_like(t), 2.35 + 0.8 * np.sin(t), 0.05 + 0.45 * np.cos(t)])
        elements.append({"type": "line", "pts": sagittal, "color": COLOR_SKELETAL, "width": 2})
        # Coronal arch
        coronal = np.column_stack([0.38 * np.cos(t), 2.35 + 0.8 * np.sin(t), np.full_like(t, 0.05)])
        elements.append({"type": "line", "pts": coronal, "color": COLOR_SKELETAL, "width": 2})

        # Facial Eye Orbits & Zygomatic Arches
        for sign in (-1, 1):
            orbit = cls._circle_3d(sign * 0.16, 2.62, 0.42, rx=0.08, ry=0.07, n=16, plane="xy")
            elements.append({"type": "loop", "pts": orbit, "color": COLOR_SKELETAL, "width": 1})
            # Zygomatic cheek arch
            zygo = cls._line_3d((sign * 0.12, 2.52, 0.40), (sign * 0.36, 2.48, 0.15), n=8)
            elements.append({"type": "line", "pts": zygo, "color": COLOR_SKELETAL, "width": 1})

        # Mandible (Jawbone) U-curve
        t_jaw = np.linspace(-np.pi * 0.4, np.pi * 0.4, 20)
        mandible = np.column_stack([0.28 * np.sin(t_jaw), 2.22 - 0.08 * np.cos(t_jaw), 0.10 + 0.32 * np.cos(t_jaw)])
        elements.append({"type": "line", "pts": mandible, "color": COLOR_SKELETAL, "width": 2})

        # ── 2. Vertebral Column (Sinusoidal Anatomical S-Curve) ──
        # Cervical lordosis, thoracic kyphosis, lumbar lordosis
        y_spine = np.linspace(2.25, 0.20, 24)
        z_spine = -0.05 + 0.12 * np.sin((y_spine - 0.5) * 2.2)
        spine_pts = np.column_stack([np.zeros_like(y_spine), y_spine, z_spine])
        elements.append({"type": "line", "pts": spine_pts, "color": COLOR_SKELETAL, "width": 3})

        # Vertebral disc plates & transverse processes
        for y_v, z_v in zip(y_spine[::2], z_spine[::2]):
            disc = cls._line_3d((-0.12, y_v, z_v), (0.12, y_v, z_v), n=6)
            elements.append({"type": "line", "pts": disc, "color": COLOR_SKELETAL, "width": 1})

        # ── 3. Thoracic Ribcage (Sternum + 10 Paired 3D Rib Arches) ──
        # Sternum (Breastbone)
        sternum = cls._line_3d((0.0, 2.05, 0.38), (0.0, 1.25, 0.34), n=12)
        elements.append({"type": "line", "pts": sternum, "color": COLOR_SKELETAL, "width": 3})

        # Clavicles (Collarbones S-Curve)
        for sign in (-1, 1):
            t_clav = np.linspace(0, 1, 15)
            x_c = sign * (0.05 + 0.95 * t_clav)
            y_c = 2.05 + 0.06 * np.sin(t_clav * np.pi)
            z_c = 0.36 - 0.22 * t_clav
            elements.append({"type": "line", "pts": np.column_stack([x_c, y_c, z_c]), "color": COLOR_SKELETAL, "width": 2})

        # 10 Paired 3D Curved Ribs
        for i in range(10):
            frac = i / 9.0
            y_rib_back = 1.95 - frac * 0.75
            y_rib_front = 1.90 - frac * 0.70
            z_back = -0.05 + 0.12 * np.sin((y_rib_back - 0.5) * 2.2)
            z_front = 0.36 - frac * 0.04
            rx = 0.35 + 0.32 * np.sin(frac * np.pi)

            for sign in (-1, 1):
                t_rib = np.linspace(0, np.pi, 20)
                # Curve starting at spine, arching outward laterally, and curving back to sternum
                x_r = sign * rx * np.sin(t_rib)
                y_r = y_rib_back + (y_rib_front - y_rib_back) * (1 - np.cos(t_rib)) * 0.5
                z_r = z_back + (z_front - z_back) * (1 - np.cos(t_rib)) * 0.5
                elements.append({"type": "line", "pts": np.column_stack([x_r, y_r, z_r]), "color": COLOR_SKELETAL, "width": 1})

        # ── 4. Pelvis & Sacrum ──
        # Iliac Crest Wings
        for sign in (-1, 1):
            t_pelv = np.linspace(0, np.pi * 0.8, 16)
            x_p = sign * (0.15 + 0.52 * np.sin(t_pelv))
            y_p = 0.10 + 0.35 * np.cos(t_pelv * 0.8)
            z_p = 0.10 * np.cos(t_pelv)
            elements.append({"type": "line", "pts": np.column_stack([x_p, y_p, z_p]), "color": COLOR_SKELETAL, "width": 2})
            # Acetabulum (Hip Socket)
            hip_ring = cls._circle_3d(sign * 0.48, 0.05, 0.02, rx=0.10, ry=0.10, n=12, plane="xy")
            elements.append({"type": "loop", "pts": hip_ring, "color": COLOR_SKELETAL, "width": 2})

        # Pubic Arch
        pubic = cls._line_3d((-0.18, -0.15, 0.15), (0.18, -0.15, 0.15), n=8)
        elements.append({"type": "line", "pts": pubic, "color": COLOR_SKELETAL, "width": 2})

        # ── 5. Upper Limbs (Humerus, Radius, Ulna, Hands) ──
        for sign in (-1, 1):
            shoulder = (sign * 1.05, 2.05, 0.12)
            elbow = (sign * 1.25, 1.05, 0.05)
            wrist = (sign * 1.38, 0.05, 0.02)
            fingers = (sign * 1.45, -0.45, 0.0)

            # Humerus (Upper arm bone)
            elements.append({"type": "line", "pts": cls._line_3d(shoulder, elbow, n=12), "color": COLOR_SKELETAL, "width": 3})
            # Radius & Ulna (Double forearm bones)
            elbow_r = (sign * 1.22, 1.05, 0.07)
            elbow_u = (sign * 1.28, 1.05, 0.03)
            wrist_r = (sign * 1.35, 0.05, 0.04)
            wrist_u = (sign * 1.41, 0.05, 0.00)
            elements.append({"type": "line", "pts": cls._line_3d(elbow_r, wrist_r, n=10), "color": COLOR_SKELETAL, "width": 2})
            elements.append({"type": "line", "pts": cls._line_3d(elbow_u, wrist_u, n=10), "color": COLOR_SKELETAL, "width": 2})
            # Hand & Metacarpals
            elements.append({"type": "line", "pts": cls._line_3d(wrist, fingers, n=8), "color": COLOR_SKELETAL, "width": 1})

        # ── 6. Lower Limbs (Femur, Patella, Tibia, Fibula, Feet) ──
        for sign in (-1, 1):
            hip = (sign * 0.48, 0.05, 0.02)
            knee = (sign * 0.40, -1.45, 0.05)
            ankle = (sign * 0.35, -2.75, 0.0)
            heel = (sign * 0.35, -2.85, -0.15)
            toe = (sign * 0.35, -2.90, 0.38)

            # Femur (Heavy Thigh Bone, angled inward)
            elements.append({"type": "line", "pts": cls._line_3d(hip, knee, n=15), "color": COLOR_SKELETAL, "width": 4})
            # Patella (Kneecap ring)
            patella = cls._circle_3d(sign * 0.40, -1.45, 0.16, rx=0.07, ry=0.07, n=12, plane="xy")
            elements.append({"type": "loop", "pts": patella, "color": COLOR_SKELETAL, "width": 2})
            # Tibia (Main shin bone)
            elements.append({"type": "line", "pts": cls._line_3d((sign * 0.38, -1.52, 0.05), (sign * 0.34, -2.72, 0.02), n=14), "color": COLOR_SKELETAL, "width": 3})
            # Fibula (Lateral slender bone)
            elements.append({"type": "line", "pts": cls._line_3d((sign * 0.45, -1.55, 0.02), (sign * 0.40, -2.70, -0.01), n=12), "color": COLOR_SKELETAL, "width": 1})
            # Foot arch (Heel to toe)
            elements.append({"type": "line", "pts": cls._line_3d(heel, toe, n=10), "color": COLOR_SKELETAL, "width": 2})

        return elements

    @classmethod
    def build_circulatory_layer(cls) -> List[Dict[str, Any]]:
        """Constructs 3D Heart chamber, Aorta, Vena Cava, Carotids, and Peripheral Vessels."""
        elements = []

        # ── 1. Anatomical Heart Chamber ──
        # Heart centered slightly left of sternum at Y=1.65
        for z_layer, r in [(0.15, 0.16), (0.24, 0.22), (0.32, 0.18)]:
            heart_ring = cls._circle_3d(-0.06, 1.65, z_layer, rx=r, ry=r * 1.15, n=16, plane="xy")
            elements.append({"type": "loop", "pts": heart_ring, "color": COLOR_CIRC_ART, "width": 2})

        # ── 2. Aortic Arch & Major Arterial Tree (Red) ──
        # Ascending aorta & arch over pulmonary artery
        t_aorta = np.linspace(0, np.pi, 16)
        x_a = -0.05 + 0.14 * np.cos(t_aorta)
        y_a = 1.82 + 0.16 * np.sin(t_aorta)
        z_a = 0.26 - 0.12 * np.cos(t_aorta)
        elements.append({"type": "line", "pts": np.column_stack([x_a, y_a, z_a]), "color": COLOR_CIRC_ART, "width": 4})

        # Descending Thoracic & Abdominal Aorta
        y_desc = np.linspace(1.82, 0.15, 20)
        aorta_desc = np.column_stack([np.full_like(y_desc, -0.02), y_desc, 0.08 + 0.04 * np.sin(y_desc)])
        elements.append({"type": "line", "pts": aorta_desc, "color": COLOR_CIRC_ART, "width": 3})

        # Common Carotid Arteries (Ascending to Brain Circle of Willis)
        for sign in (-1, 1):
            carotid = cls._line_3d((sign * 0.08, 1.95, 0.20), (sign * 0.14, 2.55, 0.24), n=10)
            elements.append({"type": "line", "pts": carotid, "color": COLOR_CIRC_ART, "width": 2})
            # Cerebral Circle of Willis
            willis = cls._circle_3d(sign * 0.12, 2.72, 0.18, rx=0.10, ry=0.08, n=12, plane="xz")
            elements.append({"type": "loop", "pts": willis, "color": COLOR_CIRC_ART, "width": 1})

        # Subclavian & Brachial Arteries (Upper Limbs)
        for sign in (-1, 1):
            brachial = cls._line_3d((sign * 0.15, 1.95, 0.20), (sign * 1.25, 1.05, 0.08), n=14)
            radial = cls._line_3d((sign * 1.25, 1.05, 0.08), (sign * 1.38, 0.05, 0.03), n=10)
            elements.append({"type": "line", "pts": brachial, "color": COLOR_CIRC_ART, "width": 2})
            elements.append({"type": "line", "pts": radial, "color": COLOR_CIRC_ART, "width": 1})

        # Renal Arteries
        for sign in (-1, 1):
            renal = cls._line_3d((-0.02, 1.05, 0.08), (sign * 0.28, 1.05, 0.02), n=6)
            elements.append({"type": "line", "pts": renal, "color": COLOR_CIRC_ART, "width": 2})

        # Common Iliac & Femoral Arteries (Lower Limbs)
        for sign in (-1, 1):
            iliac = cls._line_3d((-0.02, 0.15, 0.08), (sign * 0.44, 0.05, 0.05), n=10)
            femoral = cls._line_3d((sign * 0.44, 0.05, 0.05), (sign * 0.38, -1.45, 0.08), n=14)
            tibial = cls._line_3d((sign * 0.38, -1.45, 0.08), (sign * 0.34, -2.75, 0.02), n=12)
            elements.append({"type": "line", "pts": iliac, "color": COLOR_CIRC_ART, "width": 3})
            elements.append({"type": "line", "pts": femoral, "color": COLOR_CIRC_ART, "width": 2})
            elements.append({"type": "line", "pts": tibial, "color": COLOR_CIRC_ART, "width": 1})

        # ── 3. Venous Network (Vena Cava & Jugulars - Blue) ──
        # Inferior Vena Cava (Parallel to abdominal aorta)
        y_ivc = np.linspace(1.65, 0.15, 18)
        ivc = np.column_stack([np.full_like(y_ivc, 0.05), y_ivc, 0.09 + 0.04 * np.sin(y_ivc)])
        elements.append({"type": "line", "pts": ivc, "color": COLOR_CIRC_VEN, "width": 3})

        # Superior Vena Cava & Jugular Veins
        for sign in (-1, 1):
            jugular = cls._line_3d((sign * 0.12, 1.90, 0.22), (sign * 0.18, 2.50, 0.22), n=8)
            elements.append({"type": "line", "pts": jugular, "color": COLOR_CIRC_VEN, "width": 2})

        # Femoral & Saphenous Veins
        for sign in (-1, 1):
            fem_vein = cls._line_3d((sign * 0.48, 0.05, 0.04), (sign * 0.42, -1.45, 0.06), n=12)
            elements.append({"type": "line", "pts": fem_vein, "color": COLOR_CIRC_VEN, "width": 2})

        # Pulmonary Vascular Web (Microvasculature in both lungs)
        for sign in (-1, 1):
            for i in range(5):
                t_pulm = np.linspace(0, 1, 8)
                px = sign * (0.05 + (0.28 + 0.08 * i) * t_pulm)
                py = 1.70 + (0.20 - 0.10 * i) * t_pulm
                pz = 0.24 + 0.08 * np.sin(t_pulm * np.pi)
                col = COLOR_CIRC_ART if i % 2 == 0 else COLOR_CIRC_VEN
                elements.append({"type": "line", "pts": np.column_stack([px, py, pz]), "color": col, "width": 1})

        return elements

    @classmethod
    def build_muscular_layer(cls) -> List[Dict[str, Any]]:
        """Constructs 3D Pectoralis, Deltoids, Biceps, Abdominals, and Quadriceps."""
        elements = []

        # ── 1. Pectoralis Major (Chest Muscle Fan) ──
        for sign in (-1, 1):
            for angle in np.linspace(-0.3, 0.6, 6):
                t_pec = np.linspace(0, 1, 12)
                # Radiating from sternum out to humerus insertion
                x_pec = sign * (0.05 + 0.85 * t_pec)
                y_pec = 1.85 - 0.35 * t_pec + 0.25 * angle * (1 - t_pec)
                z_pec = 0.36 - 0.12 * t_pec + 0.06 * np.sin(t_pec * np.pi)
                elements.append({"type": "line", "pts": np.column_stack([x_pec, y_pec, z_pec]), "color": COLOR_MUSCULAR, "width": 2})

        # ── 2. Deltoids (Shoulder Muscular Caps) ──
        for sign in (-1, 1):
            for ring in [0.14, 0.20, 0.26]:
                delt_ring = cls._circle_3d(sign * 1.05, 2.05, 0.12, rx=ring, ry=ring * 1.3, n=16, plane="yz")
                elements.append({"type": "loop", "pts": delt_ring, "color": COLOR_MUSCULAR, "width": 1})

        # ── 3. Biceps & Triceps (Upper Arm Fusiform Muscle Bellies) ──
        for sign in (-1, 1):
            for offset_angle in np.linspace(0, 2 * np.pi, 6, endpoint=False):
                t_arm = np.linspace(0, 1, 12)
                # Bulging in the middle of upper arm
                r_bulge = 0.10 * np.sin(t_arm * np.pi)
                x_arm = sign * (1.05 + 0.20 * t_arm) + r_bulge * np.cos(offset_angle)
                y_arm = 2.05 - 1.00 * t_arm
                z_arm = 0.10 + 0.05 * np.cos(t_arm) + r_bulge * np.sin(offset_angle)
                elements.append({"type": "line", "pts": np.column_stack([x_arm, y_arm, z_arm]), "color": COLOR_MUSCULAR, "width": 1})

        # ── 4. Rectus Abdominis (Segmented "6-Pack" & Obliques) ──
        # Vertical tendon line (Linea Alba)
        linea_alba = cls._line_3d((0.0, 1.25, 0.35), (0.0, 0.15, 0.28), n=12)
        elements.append({"type": "line", "pts": linea_alba, "color": "#f1f5f9", "width": 2})

        # Abdominal Muscle Packs
        for y_pack in [1.10, 0.85, 0.60, 0.35]:
            for sign in (-1, 1):
                pack = cls._circle_3d(sign * 0.14, y_pack, 0.34, rx=0.10, ry=0.08, n=12, plane="xy")
                elements.append({"type": "loop", "pts": pack, "color": COLOR_MUSCULAR, "width": 2})
            # Tendinous intersection lines
            t_inter = cls._line_3d((-0.30, y_pack - 0.08, 0.32), (0.30, y_pack - 0.08, 0.32), n=8)
            elements.append({"type": "line", "pts": t_inter, "color": "#f1f5f9", "width": 1})

        # External Obliques (Lateral Abdominal Contours)
        for sign in (-1, 1):
            for i in range(4):
                y_ob = 1.05 - i * 0.20
                oblique = cls._line_3d((sign * 0.28, y_ob, 0.30), (sign * 0.55, y_ob - 0.12, 0.05), n=8)
                elements.append({"type": "line", "pts": oblique, "color": COLOR_MUSCULAR, "width": 1})

        # ── 5. Quadriceps Femoris (Thigh Muscle Complex) ──
        for sign in (-1, 1):
            for angle in np.linspace(0, 2 * np.pi, 8, endpoint=False):
                t_leg = np.linspace(0, 1, 14)
                # Volumetric thigh muscle belly bulging at proximal 1/3
                bulge = 0.16 * np.sin(t_leg * np.pi)
                x_leg = sign * (0.48 - 0.08 * t_leg) + bulge * np.cos(angle)
                y_leg = 0.05 - 1.50 * t_leg
                z_leg = 0.05 + bulge * np.sin(angle)
                elements.append({"type": "line", "pts": np.column_stack([x_leg, y_leg, z_leg]), "color": COLOR_MUSCULAR, "width": 1})

        # ── 6. Gastrocnemius & Soleus (Calf Muscle Complex) ──
        for sign in (-1, 1):
            for angle in np.linspace(0, 2 * np.pi, 6, endpoint=False):
                t_calf = np.linspace(0, 1, 12)
                # Bulge on posterior/lateral upper calf
                bulge_c = 0.12 * np.sin(t_calf * np.pi * 0.8)
                x_c = sign * (0.40 - 0.05 * t_calf) + bulge_c * np.cos(angle)
                y_c = -1.55 - 1.20 * t_calf
                z_c = -0.02 - 0.08 * np.sin(t_calf * np.pi) + bulge_c * np.sin(angle)
                elements.append({"type": "line", "pts": np.column_stack([x_c, y_c, z_c]), "color": COLOR_MUSCULAR, "width": 1})

        return elements

    @classmethod
    def build_visceral_layer(cls) -> List[Dict[str, Any]]:
        """Constructs 3D Internal Organs: Lungs, Liver, Stomach, Kidneys, Brain."""
        elements = []

        # ── 1. Left & Right Lungs (3D Lobar Envelopes) ──
        for sign, lobes in [(-1, 2), (1, 3)]:
            cx = sign * 0.32
            # Longitudinal lung ribs
            for theta in np.linspace(0, 2 * np.pi, 8, endpoint=False):
                t_lung = np.linspace(0, 1, 14)
                r = 0.18 * np.sin(t_lung * np.pi)
                # Notch on left lung for the heart
                if sign == -1:
                    r *= 0.85
                lx = cx + r * np.cos(theta)
                ly = 2.00 - 0.75 * t_lung
                lz = 0.20 + r * np.sin(theta)
                elements.append({"type": "line", "pts": np.column_stack([lx, ly, lz]), "color": COLOR_VISCERAL, "width": 1})

            # Horizontal lung contour rings
            for y_l in [1.85, 1.65, 1.45]:
                l_ring = cls._circle_3d(cx, y_l, 0.20, rx=0.18, ry=0, rz=0.14, n=16, plane="xz")
                elements.append({"type": "loop", "pts": l_ring, "color": COLOR_VISCERAL, "width": 1})

        # ── 2. Liver (Right Upper Quadrant Wedge) ──
        for y_liv in [1.25, 1.15, 1.05]:
            liv_ring = cls._circle_3d(0.24, y_liv, 0.22, rx=0.22, ry=0.14, n=16, plane="xy")
            elements.append({"type": "loop", "pts": liv_ring, "color": "#10b981", "width": 2})

        # ── 3. Stomach (J-Shaped Left Upper Quadrant Organ) ──
        t_stom = np.linspace(0, np.pi * 0.9, 16)
        x_st = -0.12 - 0.16 * np.cos(t_stom)
        y_st = 1.25 - 0.25 * np.sin(t_stom)
        z_st = 0.22 + 0.08 * np.cos(t_stom)
        elements.append({"type": "line", "pts": np.column_stack([x_st, y_st, z_st]), "color": "#f59e0b", "width": 3})

        # ── 4. Kidneys (Bilateral Retroperitoneal Bean Shapes) ──
        for sign in (-1, 1):
            kidney = cls._circle_3d(sign * 0.28, 0.90, -0.06, rx=0.08, ry=0.14, n=14, plane="xy")
            elements.append({"type": "loop", "pts": kidney, "color": "#8b5cf6", "width": 2})

        # ── 5. Brain (Cerebral Hemispheres in Cranium) ──
        for sign in (-1, 1):
            brain_ring1 = cls._circle_3d(sign * 0.14, 2.75, 0.06, rx=0.14, ry=0.20, n=16, plane="xy")
            brain_ring2 = cls._circle_3d(sign * 0.14, 2.75, 0.06, rx=0.14, ry=0, rz=0.20, n=16, plane="xz")
            elements.append({"type": "loop", "pts": brain_ring1, "color": "#ec4899", "width": 1})
            elements.append({"type": "loop", "pts": brain_ring2, "color": "#ec4899", "width": 1})

        return elements


# ─────────────────────────────────────────────────────────────────────────────
# 4. PRE-CONFIGURED CLINICAL ISSUES DATASET (NOT BODY PARTS)
# ─────────────────────────────────────────────────────────────────────────────
INITIAL_CLINICAL_ISSUES: List[ClinicalIssue] = [
    ClinicalIssue(
        id="ISS-01",
        name="Acute Myocardial Infarction (LAD Occlusion)",
        system="Circulatory",
        severity="CRITICAL",
        coord_3d=np.array([-0.08, 1.62, 0.32]),
        icd10="I21.0 - ST-Elevation Myocardial Infarction",
        symptoms="Acute retrosternal crushing pain, diaphoresis, ST-segment elevation in V1-V4.",
        intervention="Emergency percutaneous coronary intervention (PCI) with drug-eluting stent placement under AR holographic fluoroscopy guidance."
    ),
    ClinicalIssue(
        id="ISS-02",
        name="Displaced Midshaft Femur Fracture",
        system="Skeletal",
        severity="HIGH",
        coord_3d=np.array([-0.42, -0.75, 0.08]),
        icd10="S72.301A - Transverse Femur Fracture",
        symptoms="Severe thigh deformity, extensive soft-tissue hematoma, inability to bear weight.",
        intervention="Closed reduction and reamed intramedullary interlocking nail fixation with AR anatomical alignment overlay."
    ),
    ClinicalIssue(
        id="ISS-03",
        name="Abdominal Aortic Aneurysm (AAA)",
        system="Circulatory",
        severity="CRITICAL",
        coord_3d=np.array([-0.02, 0.65, 0.12]),
        icd10="I71.4 - Infrarenal Aortic Aneurysm Without Rupture",
        symptoms="Pulsatile abdominal mass, lower back dull ache; luminal diameter = 5.6 cm.",
        intervention="Endovascular Aneurysm Repair (EVAR) with bifurcated modular stent-graft under 3D AR navigation."
    ),
    ClinicalIssue(
        id="ISS-04",
        name="Right Tension Pneumothorax",
        system="Visceral",
        severity="CRITICAL",
        coord_3d=np.array([0.35, 1.55, 0.24]),
        icd10="J93.0 - Tension Pneumothorax",
        symptoms="Hyper-resonant percussion on right thorax, tracheal deviation, acute hypoxia.",
        intervention="Immediate 14G needle decompression in 2nd intercostal space, followed by tube thoracostomy."
    ),
    ClinicalIssue(
        id="ISS-05",
        name="L4-L5 Lumbar Disc Herniation",
        system="Skeletal",
        severity="MODERATE",
        coord_3d=np.array([0.00, 0.45, -0.08]),
        icd10="M51.26 - Intervertebral Disc Disorder with Radiculopathy",
        symptoms="Sciatica radiating along left L5 dermatome, positive straight leg raise, weakness in big toe dorsiflexion.",
        intervention="Minimally invasive endoscopic microdiscectomy guided by stereoscopic 3D spine visualization."
    ),
    ClinicalIssue(
        id="ISS-06",
        name="Distal Biceps Tendon Full Rupture",
        system="Muscular",
        severity="MODERATE",
        coord_3d=np.array([1.25, 0.95, 0.12]),
        icd10="S46.211A - Strain of Extensor Muscle of Forearm",
        symptoms="Audible pop during heavy lifting, 'Popeye deformity' with proximal muscle retraction, weak supination.",
        intervention="Anatomical distal biceps reinsertion onto radial tuberosity using cortical button and interference screw."
    ),
    ClinicalIssue(
        id="ISS-07",
        name="Hepatic Focal Lesion (Segment VII)",
        system="Visceral",
        severity="HIGH",
        coord_3d=np.array([0.28, 1.15, 0.22]),
        icd10="C22.0 - Hepatocellular Carcinoma",
        symptoms="Alpha-fetoprotein elevation, arterial phase hyper-enhancement with venous washout.",
        intervention="Laparoscopic ultrasound-guided microwave ablation with 3D AR margin overlay planning."
    ),
    ClinicalIssue(
        id="ISS-08",
        name="Deep Vein Thrombosis (Right Common Femoral)",
        system="Circulatory",
        severity="HIGH",
        coord_3d=np.array([0.46, 0.08, 0.06]),
        icd10="I82.411 - Acute Femoral Vein Thrombosis",
        symptoms="Unilateral right lower extremity edema, tenderness along femoral canal, elevated D-Dimer.",
        intervention="Targeted catheter-directed thrombolysis (CDT) and therapeutic anticoagulation monitoring."
    ),
    ClinicalIssue(
        id="ISS-09",
        name="Grade III Rectus Femoris Muscle Tear",
        system="Muscular",
        severity="MODERATE",
        coord_3d=np.array([-0.40, -0.60, 0.22]),
        icd10="S76.111A - Strain of Right Quadriceps Muscle",
        symptoms="Focal palpable muscle defect, large intramuscular hematoma, severe pain on resisted knee extension.",
        intervention="Platelet-Rich Plasma (PRP) ultrasound-guided infiltration and controlled rehabilitation protocol."
    ),
    ClinicalIssue(
        id="ISS-10",
        name="Depressed Temporal Skull Fracture & Epidural Bleed",
        system="Skeletal",
        severity="CRITICAL",
        coord_3d=np.array([0.34, 2.70, 0.18]),
        icd10="S02.111A - Fracture of Skull with Intracranial Injury",
        symptoms="Battle sign, lucid interval followed by rapid GCS drop, anisocoria (right pupil dilated).",
        intervention="Emergency osteoplastic craniotomy and evacuation of epidural hematoma with cranial reconstruction."
    ),
]


# ─────────────────────────────────────────────────────────────────────────────
# 5. 3D CAMERA & PROJECTION SYSTEM (SUPPORTS AR HUD & VR STEREOSCOPIC 3D)
# ─────────────────────────────────────────────────────────────────────────────
class Camera3D:
    """
    Handles 3D transformation matrices, orbital rotation (Yaw/Pitch),
    perspective projection, and optical binocular parallax for VR stereoscopy.
    """

    def __init__(self, fov: float = 4.2, zoom: float = 135.0) -> None:
        self.yaw: float = 0.35          # Horizontal orbit angle in radians
        self.pitch: float = 0.08        # Vertical tilt angle in radians
        self.zoom: float = zoom         # Projection magnification
        self.pan_x: float = 0.0         # Screen-space pan X
        self.pan_y: float = 0.0         # Screen-space pan Y
        self.fov: float = fov           # Field of view perspective factor
        self.stereo_ipd: float = 0.045  # Interpupillary eye separation for VR mode

    def reset(self) -> None:
        """Resets camera to default anterior anatomical viewpoint."""
        self.yaw = 0.0
        self.pitch = 0.0
        self.zoom = 135.0
        self.pan_x = 0.0
        self.pan_y = 0.0

    def rotate(self, delta_yaw: float, delta_pitch: float) -> None:
        """Rotates camera angles clamped to avoid gimbal flip."""
        self.yaw += delta_yaw
        self.pitch = np.clip(self.pitch + delta_pitch, -np.pi * 0.45, np.pi * 0.45)

    def pan(self, dx: float, dy: float) -> None:
        """Pans camera in screen space."""
        self.pan_x += dx
        self.pan_y += dy

    def zoom_by(self, factor: float) -> None:
        """Adjusts zoom magnification clamped to safe bounds."""
        self.zoom = np.clip(self.zoom * factor, 40.0, 450.0)

    def project_points(self, points: np.ndarray, width: float, height: float,
                       eye_offset: float = 0.0) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Projects 3D points (N, 3) to 2D screen coordinates (sx, sy) and camera depth (z_cam).
        Includes eye_offset angle for VR binocular stereoscopy.
        """
        if len(points) == 0:
            return np.empty((0,)), np.empty((0,)), np.empty((0,))

        # Effective yaw including stereoscopic eye angle
        effective_yaw = self.yaw + eye_offset

        cy, sy = np.cos(effective_yaw), np.sin(effective_yaw)
        cp, sp = np.cos(self.pitch), np.sin(self.pitch)

        # 3D Rotation matrices
        Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]], dtype=np.float32)
        Rx = np.array([[1, 0, 0], [0, cp, -sp], [0, sp, cp]], dtype=np.float32)

        # Apply transformation
        rot = (points @ Ry.T) @ Rx.T

        # Perspective division
        z_cam = rot[:, 2] + self.fov
        z_safe = np.maximum(z_cam, 0.2)
        perspective_scale = (self.fov / z_safe) * self.zoom

        # Screen coordinates
        sx = (width / 2.0) + rot[:, 0] * perspective_scale + self.pan_x
        sy = (height / 2.0) - rot[:, 1] * perspective_scale + self.pan_y

        return sx, sy, rot[:, 2]

    def unproject_screen_to_world(self, sx: float, sy: float, width: float, height: float,
                                   assumed_z: float = 0.20) -> np.ndarray:
        """
        Unprojects a 2D screen coordinate (sx, sy) back into 3D world space (X, Y, Z)
        on the anterior anatomical surface plane.
        """
        z_cam = assumed_z + self.fov
        scale = (self.fov / max(z_cam, 0.1)) * self.zoom

        rot_x = (sx - (width / 2.0) - self.pan_x) / scale
        rot_y = ((height / 2.0) + self.pan_y - sy) / scale
        rot_z = assumed_z

        cy, sy_ = np.cos(self.yaw), np.sin(self.yaw)
        cp, sp = np.cos(self.pitch), np.sin(self.pitch)
        Ry = np.array([[cy, 0, sy_], [0, 1, 0], [-sy_, 0, cy]], dtype=np.float32)
        Rx = np.array([[1, 0, 0], [0, cp, -sp], [0, sp, cp]], dtype=np.float32)

        rot_vec = np.array([rot_x, rot_y, rot_z], dtype=np.float32)
        world_pos = rot_vec @ Rx @ Ry
        return world_pos


# ─────────────────────────────────────────────────────────────────────────────
# 6. MAIN APPLICATION: BIOVISION 3D (AR/VR MEDICAL VISUALIZER)
# ─────────────────────────────────────────────────────────────────────────────
class BioVision3DApp:
    """
    Main GUI application managing the 3D rendering pipeline, multi-layer
    compositing, clinical issues interaction, AR HUD, and VR Stereoscopic mode.
    """

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("BioVision 3D — Holographic AR/VR Medical Anatomy Visualizer")
        self.root.geometry("1340x840")
        self.root.minsize(1050, 700)
        self.root.configure(bg=BG_COLOR)

        # ── State Variables ──
        self.camera = Camera3D()
        self.vr_mode: bool = False                 # Toggle between AR HUD and VR Stereoscopic
        self.auto_orbit: bool = False              # Holographic turntable animation
        self.pin_mode: bool = False                # 3D click-to-pin mode for runtime annotation
        self.selected_issue: Optional[ClinicalIssue] = None
        self.active_issues: List[ClinicalIssue] = list(INITIAL_CLINICAL_ISSUES)

        # Layer visibility flags
        self.show_skeletal = tk.BooleanVar(value=True)
        self.show_circulatory = tk.BooleanVar(value=True)
        self.show_muscular = tk.BooleanVar(value=False)   # off by default to reveal inner structures
        self.show_visceral = tk.BooleanVar(value=True)
        self.show_ground_grid = tk.BooleanVar(value=True)

        # Layer Opacity sliders (for multi-layer blending)
        self.opacity_skeletal = tk.DoubleVar(value=1.0)
        self.opacity_circulatory = tk.DoubleVar(value=1.0)
        self.opacity_muscular = tk.DoubleVar(value=0.7)
        self.opacity_visceral = tk.DoubleVar(value=0.85)

        # Mouse tracking for 3D navigation
        self._last_mouse_x: int = 0
        self._last_mouse_y: int = 0
        self._drag_button: Optional[int] = None

        # Build 3D Anatomical Geometries
        self._generate_anatomy_models()

        # Build UI layout
        self._build_top_header()
        self._build_main_layout()
        self._build_bottom_telemetry_bar()

        # Bind events
        self._bind_canvas_events()

        # Start animation loop
        self.root.after(30, self._render_frame)
        self.root.after(50, self._auto_orbit_tick)

    # ── Geometry Generation ──────────────────
    def _generate_anatomy_models(self) -> None:
        """Constructs all 4 layers from the 3D parametric engine."""
        self.geom_skeletal = Anatomy3DEngine.build_skeletal_layer()
        self.geom_circulatory = Anatomy3DEngine.build_circulatory_layer()
        self.geom_muscular = Anatomy3DEngine.build_muscular_layer()
        self.geom_visceral = Anatomy3DEngine.build_visceral_layer()

    # ═══════════════════════════════════════════
    # UI CONSTRUCTION
    # ═══════════════════════════════════════════
    def _build_top_header(self) -> None:
        """Creates top cybernetic toolbar with reality mode switch and controls."""
        header = tk.Frame(self.root, bg=PANEL_BG, height=54, padx=14, pady=6)
        header.pack(side=tk.TOP, fill=tk.X)

        # Brand / Logo
        logo_frame = tk.Frame(header, bg=PANEL_BG)
        logo_frame.pack(side=tk.LEFT, padx=(0, 25))

        tk.Label(
            logo_frame, text="⬡ BIOVISION 3D",
            bg=PANEL_BG, fg=ACCENT_CYAN,
            font=("Segoe UI", 13, "bold")
        ).pack(side=tk.TOP, anchor="w")

        tk.Label(
            logo_frame, text="HOLOGRAPHIC AR/VR MEDICAL VISUALIZER | GROUP 6",
            bg=PANEL_BG, fg=TEXT_MUTED,
            font=("Segoe UI", 7, "bold")
        ).pack(side=tk.TOP, anchor="w")

        # Action Buttons
        btn_style = dict(
            bg=PANEL_ALT_BG, fg=TEXT_PRIMARY, activebackground="#1e293b",
            activeforeground=ACCENT_CYAN, relief=tk.FLAT, padx=10, pady=5,
            font=("Segoe UI", 9, "bold"), cursor="hand2", highlightthickness=1,
            highlightbackground=BORDER_COLOR
        )

        # VR Mode Toggle Button
        self.btn_vr_toggle = tk.Button(
            header, text="🥽 SWITCH TO VR STEREOSCOPIC",
            command=self._toggle_vr_mode,
            bg="#312e81", fg="#a5b4fc", activebackground="#4338ca",
            activeforeground="#ffffff", relief=tk.FLAT, padx=12, pady=5,
            font=("Segoe UI", 9, "bold"), cursor="hand2", highlightthickness=1,
            highlightbackground="#6366f1"
        )
        self.btn_vr_toggle.pack(side=tk.LEFT, padx=6)

        # Auto-Orbit Showcase Button
        self.btn_orbit = tk.Button(
            header, text="🔄 AUTO-ORBIT (HOLOGRAPHIC)",
            command=self._toggle_auto_orbit, **btn_style
        )
        self.btn_orbit.pack(side=tk.LEFT, padx=6)

        # Reset Camera
        tk.Button(
            header, text="🎯 RESET CAMERA",
            command=self.camera.reset, **btn_style
        ).pack(side=tk.LEFT, padx=6)

        # Pin directly on 3D Anatomy Surface
        self.btn_pin_mode = tk.Button(
            header, text="📍 PIN ON 3D BODY",
            command=self._toggle_pin_mode,
            bg="#b45309", fg="#fef3c7", activebackground="#d97706",
            activeforeground="#ffffff", relief=tk.FLAT, padx=10, pady=5,
            font=("Segoe UI", 9, "bold"), cursor="hand2", highlightthickness=1,
            highlightbackground="#f59e0b"
        )
        self.btn_pin_mode.pack(side=tk.LEFT, padx=5)

        # Add Custom Clinical Issue via Form
        tk.Button(
            header, text="➕ ADD ISSUE",
            command=self._open_add_issue_dialog,
            bg="#065f46", fg="#6ee7b7", activebackground="#047857",
            activeforeground="#ffffff", relief=tk.FLAT, padx=10, pady=5,
            font=("Segoe UI", 9, "bold"), cursor="hand2", highlightthickness=1,
            highlightbackground="#10b981"
        ).pack(side=tk.LEFT, padx=5)

        # Load Case File (JSON)
        tk.Button(
            header, text="📂 LOAD CASE (JSON)",
            command=self._load_case_json, **btn_style
        ).pack(side=tk.LEFT, padx=5)

        # Save Case File (JSON)
        tk.Button(
            header, text="💾 SAVE CASE (JSON)",
            command=self._save_case_json, **btn_style
        ).pack(side=tk.LEFT, padx=5)

        # Export Viewport Snapshot
        tk.Button(
            header, text="📷 SNAPSHOT",
            command=self._export_snapshot, **btn_style
        ).pack(side=tk.LEFT, padx=5)

    def _build_main_layout(self) -> None:
        """Constructs split-pane layout: 3D viewport canvas + clinical inspector sidebar."""
        main_container = tk.Frame(self.root, bg=BG_COLOR)
        main_container.pack(fill=tk.BOTH, expand=True)

        # ── Left: Interactive 3D Canvas ──
        canvas_frame = tk.Frame(main_container, bg=CANVAS_BG)
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(
            canvas_frame, bg=CANVAS_BG, highlightthickness=0,
            cursor="crosshair"
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # ── Right: Sidebar (Layers & Clinical Issues Inspector) ──
        sidebar = tk.Frame(main_container, bg=PANEL_BG, width=380, padx=12, pady=10)
        sidebar.pack(side=tk.RIGHT, fill=tk.Y)
        sidebar.pack_propagate(False)

        # --- Section 1: 4 Overlapping Anatomical Layers ---
        layer_hdr = tk.Label(
            sidebar, text="── ANATOMICAL LAYERS (OVERLAY) ──",
            bg=PANEL_BG, fg=ACCENT_CYAN, font=("Segoe UI", 9, "bold")
        )
        layer_hdr.pack(anchor="w", pady=(0, 6))

        layers_box = tk.Frame(sidebar, bg=PANEL_ALT_BG, padx=8, pady=6, highlightthickness=1, highlightbackground=BORDER_COLOR)
        layers_box.pack(fill=tk.X, pady=(0, 10))

        layers_info = [
            ("🦴 Skeletal Layer (Bones & Joints)", self.show_skeletal, COLOR_SKELETAL),
            ("🫀 Circulatory Layer (Arteries & Veins)", self.show_circulatory, COLOR_CIRC_ART),
            ("💪 Muscular Layer (Muscle Contours)", self.show_muscular, COLOR_MUSCULAR),
            ("🧠 Visceral Layer (Internal Organs)", self.show_visceral, COLOR_VISCERAL),
        ]

        for text, var, col in layers_info:
            row = tk.Frame(layers_box, bg=PANEL_ALT_BG)
            row.pack(fill=tk.X, pady=2)
            chk = tk.Checkbutton(
                row, text=text, variable=var,
                bg=PANEL_ALT_BG, fg=TEXT_PRIMARY, selectcolor=BG_COLOR,
                activebackground=PANEL_ALT_BG, activeforeground=col,
                font=("Segoe UI", 9, "bold"), cursor="hand2"
            )
            chk.pack(side=tk.LEFT)

        # Ground Grid Toggle
        chk_grid = tk.Checkbutton(
            layers_box, text="🌐 Holographic Coordinate Ground Grid",
            variable=self.show_ground_grid,
            bg=PANEL_ALT_BG, fg=TEXT_MUTED, selectcolor=BG_COLOR,
            activebackground=PANEL_ALT_BG, activeforeground=ACCENT_CYAN,
            font=("Segoe UI", 8), cursor="hand2"
        )
        chk_grid.pack(anchor="w", pady=(2, 0))

        # --- Section 2: Clinical Diagnostic Issues (NOT body parts) ---
        issues_hdr = tk.Label(
            sidebar, text="── CLINICAL ISSUES & PATHOLOGY ──",
            bg=PANEL_BG, fg=ACCENT_YELLOW, font=("Segoe UI", 9, "bold")
        )
        issues_hdr.pack(anchor="w", pady=(4, 4))

        # Treeview list of clinical issues
        tree_frame = tk.Frame(sidebar, bg=PANEL_ALT_BG)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Issues.Treeview",
            background=PANEL_ALT_BG, foreground=TEXT_PRIMARY,
            fieldbackground=PANEL_ALT_BG, borderwidth=0,
            font=("Segoe UI", 9), rowheight=24
        )
        style.map("Issues.Treeview", background=[("selected", "#1e3a8a")])

        self.issues_tree = ttk.Treeview(
            tree_frame, columns=("id", "severity", "name"),
            show="headings", style="Issues.Treeview", selectmode="browse"
        )
        self.issues_tree.heading("id", text="ID")
        self.issues_tree.heading("severity", text="SEVERITY")
        self.issues_tree.heading("name", text="PATHOLOGY")

        self.issues_tree.column("id", width=55, stretch=False)
        self.issues_tree.column("severity", width=80, stretch=False)
        self.issues_tree.column("name", width=210)

        tree_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.issues_tree.yview)
        self.issues_tree.configure(yscrollcommand=tree_scroll.set)

        self.issues_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.issues_tree.bind("<<TreeviewSelect>>", self._on_issue_selected_from_list)

        self._refresh_issues_tree()

        # --- Section 3: Diagnostic Telemetry Inspector Card ---
        card_lbl = tk.Label(
            sidebar, text="── DIAGNOSTIC TELEMETRY CARD ──",
            bg=PANEL_BG, fg=ACCENT_GREEN, font=("Segoe UI", 9, "bold")
        )
        card_lbl.pack(anchor="w", pady=(2, 4))

        self.card_frame = tk.Frame(
            sidebar, bg=PANEL_ALT_BG, padx=10, pady=8,
            highlightthickness=1, highlightbackground=BORDER_COLOR
        )
        self.card_frame.pack(fill=tk.X)

        self.lbl_card_title = tk.Label(
            self.card_frame, text="Select an issue to inspect telemetry",
            bg=PANEL_ALT_BG, fg=TEXT_MUTED, font=("Segoe UI", 9, "bold"),
            wraplength=340, justify="left"
        )
        self.lbl_card_title.pack(anchor="w")

        self.lbl_card_icd = tk.Label(
            self.card_frame, text="", bg=PANEL_ALT_BG, fg=ACCENT_CYAN,
            font=("Consolas", 8), justify="left"
        )
        self.lbl_card_icd.pack(anchor="w", pady=(2, 0))

        self.lbl_card_details = tk.Label(
            self.card_frame, text="", bg=PANEL_ALT_BG, fg=TEXT_PRIMARY,
            font=("Segoe UI", 8), wraplength=340, justify="left"
        )
        self.lbl_card_details.pack(anchor="w", pady=(4, 0))

        self.lbl_card_plan = tk.Label(
            self.card_frame, text="", bg=PANEL_ALT_BG, fg="#86efac",
            font=("Segoe UI", 8, "italic"), wraplength=340, justify="left"
        )
        self.lbl_card_plan.pack(anchor="w", pady=(4, 0))

        # Action Button Row (Focus & Delete)
        btn_row = tk.Frame(self.card_frame, bg=PANEL_ALT_BG)
        btn_row.pack(fill=tk.X, pady=(6, 0))

        # Focus Issue Camera Button
        self.btn_focus_issue = tk.Button(
            btn_row, text="🎯 FOCUS CAMERA",
            command=self._focus_on_selected_issue,
            bg="#1e293b", fg=ACCENT_CYAN, activebackground="#334155",
            activeforeground="#ffffff", relief=tk.FLAT, padx=8, pady=4,
            font=("Segoe UI", 8, "bold"), cursor="hand2", state=tk.DISABLED
        )
        self.btn_focus_issue.pack(side=tk.LEFT, padx=(0, 6))

        # Delete Selected Issue Button
        self.btn_delete_issue = tk.Button(
            btn_row, text="🗑 DELETE ISSUE",
            command=self._delete_selected_issue,
            bg="#7f1d1d", fg="#fca5a5", activebackground="#991b1b",
            activeforeground="#ffffff", relief=tk.FLAT, padx=8, pady=4,
            font=("Segoe UI", 8, "bold"), cursor="hand2", state=tk.DISABLED
        )
        self.btn_delete_issue.pack(side=tk.LEFT)

    def _build_bottom_telemetry_bar(self) -> None:
        """Creates the bottom status bar displaying camera telemetry and reality state."""
        bar = tk.Frame(self.root, bg="#050811", height=28, padx=12, pady=4)
        bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.lbl_mode_status = tk.Label(
            bar, text="MODE: 📡 AR HOLOGRAPHIC HUD ACTIVE",
            bg="#050811", fg=ACCENT_GREEN, font=("Consolas", 9, "bold")
        )
        self.lbl_mode_status.pack(side=tk.LEFT)

        self.lbl_telemetry = tk.Label(
            bar, text="YAW: 0.0° | PITCH: 0.0° | ZOOM: 135% | LAYERS: 3/4 ACTIVE",
            bg="#050811", fg=TEXT_MUTED, font=("Consolas", 9)
        )
        self.lbl_telemetry.pack(side=tk.RIGHT)

    # ═══════════════════════════════════════════
    # INTERACTION & EVENT BINDINGS
    # ═══════════════════════════════════════════
    def _bind_canvas_events(self) -> None:
        """Binds mouse gestures for 3D orbital navigation and issue picking."""
        self.canvas.bind("<ButtonPress-1>", self._on_mouse_down_left)
        self.canvas.bind("<B1-Motion>", self._on_mouse_drag_orbit)
        self.canvas.bind("<ButtonPress-3>", self._on_mouse_down_right)
        self.canvas.bind("<B3-Motion>", self._on_mouse_drag_pan)
        self.canvas.bind("<MouseWheel>", self._on_mouse_wheel)
        self.canvas.bind("<ButtonRelease-1>", self._on_mouse_release)
        self.canvas.bind("<ButtonRelease-3>", self._on_mouse_release)

    def _on_mouse_down_left(self, event: tk.Event) -> None:
        # Check if Pin Mode is active for runtime 3D placement
        if self.pin_mode:
            w = self.canvas.winfo_width()
            h = self.canvas.winfo_height()
            world_coord = self.camera.unproject_screen_to_world(event.x, event.y, w, h)
            self._toggle_pin_mode()
            self._open_add_issue_dialog(prefill_coord=world_coord)
            return

        self._last_mouse_x = event.x
        self._last_mouse_y = event.y
        self._drag_button = 1
        # Check if clicked directly on an issue pin in 3D
        self._pick_issue_at_screen_pos(event.x, event.y)

    def _on_mouse_drag_orbit(self, event: tk.Event) -> None:
        if self._drag_button == 1:
            dx = event.x - self._last_mouse_x
            dy = event.y - self._last_mouse_y
            self._last_mouse_x = event.x
            self._last_mouse_y = event.y
            # Orbit rotation sensitivity
            self.camera.rotate(delta_yaw=dx * 0.008, delta_pitch=dy * 0.008)

    def _on_mouse_down_right(self, event: tk.Event) -> None:
        self._last_mouse_x = event.x
        self._last_mouse_y = event.y
        self._drag_button = 3

    def _on_mouse_drag_pan(self, event: tk.Event) -> None:
        if self._drag_button == 3:
            dx = event.x - self._last_mouse_x
            dy = event.y - self._last_mouse_y
            self._last_mouse_x = event.x
            self._last_mouse_y = event.y
            self.camera.pan(dx=dx, dy=dy)

    def _on_mouse_release(self, _event: tk.Event) -> None:
        self._drag_button = None

    def _on_mouse_wheel(self, event: tk.Event) -> None:
        # Windows mouse wheel delta
        factor = 1.10 if event.delta > 0 else 0.90
        self.camera.zoom_by(factor)

    # ═══════════════════════════════════════════
    # REALITY MODE SWITCH (AR vs VR)
    # ═══════════════════════════════════════════
    def _toggle_vr_mode(self) -> None:
        """Toggles between single-viewport AR HUD and dual-viewport VR Stereoscopic 3D."""
        self.vr_mode = not self.vr_mode
        if self.vr_mode:
            self.btn_vr_toggle.config(
                text="📡 SWITCH TO AR HOLOGRAPHIC",
                bg="#065f46", fg="#6ee7b7", highlightbackground="#10b981"
            )
            self.lbl_mode_status.config(
                text="MODE: 🥽 VR STEREOSCOPIC 3D (DUAL-VIEWPORT ACTIVE)",
                fg="#a5b4fc"
            )
        else:
            self.btn_vr_toggle.config(
                text="🥽 SWITCH TO VR STEREOSCOPIC",
                bg="#312e81", fg="#a5b4fc", highlightbackground="#6366f1"
            )
            self.lbl_mode_status.config(
                text="MODE: 📡 AR HOLOGRAPHIC HUD ACTIVE",
                fg=ACCENT_GREEN
            )

    def _toggle_auto_orbit(self) -> None:
        """Toggles automatic 3D rotation."""
        self.auto_orbit = not self.auto_orbit
        if self.auto_orbit:
            self.btn_orbit.config(bg="#065f46", fg=ACCENT_GREEN)
        else:
            self.btn_orbit.config(bg=PANEL_ALT_BG, fg=TEXT_PRIMARY)

    def _auto_orbit_tick(self) -> None:
        """Increments rotation when auto-orbit is enabled."""
        if self.auto_orbit and self._drag_button is None:
            self.camera.rotate(delta_yaw=0.015, delta_pitch=0.0)
        self.root.after(30, self._auto_orbit_tick)

    # ═══════════════════════════════════════════
    # CLINICAL ISSUES MANAGEMENT & SELECTION
    # ═══════════════════════════════════════════
    def _refresh_issues_tree(self) -> None:
        """Refreshes the Treeview list of clinical issues."""
        for item in self.issues_tree.get_children():
            self.issues_tree.delete(item)

        for issue in self.active_issues:
            self.issues_tree.insert(
                "", tk.END, iid=issue.id,
                values=(issue.id, issue.severity, issue.name)
            )

    def _on_issue_selected_from_list(self, _event: tk.Event) -> None:
        """Triggers when an issue is highlighted in the sidebar list."""
        selected = self.issues_tree.selection()
        if not selected:
            return
        issue_id = selected[0]
        for issue in self.active_issues:
            if issue.id == issue_id:
                self.selected_issue = issue
                self._update_diagnostic_card(issue)
                break

    def _update_diagnostic_card(self, issue: ClinicalIssue) -> None:
        """Populates the sidebar diagnostic card with clinical pathology data."""
        self.lbl_card_title.config(
            text=f"[{issue.severity}] {issue.name}",
            fg=issue.severity_color
        )
        self.lbl_card_icd.config(
            text=f"ICD-10: {issue.icd10}\nSYSTEM: {issue.system.upper()} | COORD: ({issue.coord_3d[0]:.2f}, {issue.coord_3d[1]:.2f}, {issue.coord_3d[2]:.2f})"
        )
        self.lbl_card_details.config(
            text=f"SYMPTOMS:\n{issue.symptoms}"
        )
        self.lbl_card_plan.config(
            text=f"AR SURGICAL GUIDANCE:\n{issue.intervention}"
        )
        self.btn_focus_issue.config(state=tk.NORMAL)
        self.btn_delete_issue.config(state=tk.NORMAL)

    def _focus_on_selected_issue(self) -> None:
        """Animates camera to center and zoom in on the chosen pathology."""
        if not self.selected_issue:
            return
        target = self.selected_issue.coord_3d
        # Align yaw toward target
        target_yaw = -math.atan2(target[0], max(target[2] + 0.1, 0.1))
        self.camera.yaw = target_yaw
        self.camera.pitch = 0.05
        self.camera.pan_x = 0
        self.camera.pan_y = target[1] * self.camera.zoom * 0.7
        self.camera.zoom = 180.0

    def _delete_selected_issue(self) -> None:
        """Deletes the currently selected clinical issue in runtime."""
        if not self.selected_issue:
            return
        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to remove issue:\n'{self.selected_issue.name}'?",
            parent=self.root
        )
        if not confirm:
            return

        self.active_issues = [iss for iss in self.active_issues if iss.id != self.selected_issue.id]
        self.selected_issue = None
        self._refresh_issues_tree()

        # Reset Card
        self.lbl_card_title.config(text="Select an issue to inspect telemetry", fg=TEXT_MUTED)
        self.lbl_card_icd.config(text="")
        self.lbl_card_details.config(text="")
        self.lbl_card_plan.config(text="")
        self.btn_focus_issue.config(state=tk.DISABLED)
        self.btn_delete_issue.config(state=tk.DISABLED)

    def _toggle_pin_mode(self) -> None:
        """Toggles interactive 3D click-to-pin mode on/off."""
        self.pin_mode = not self.pin_mode
        if self.pin_mode:
            self.btn_pin_mode.config(
                text="📍 CANCEL PIN MODE",
                bg="#f59e0b", fg="#000000", highlightbackground="#fbbf24"
            )
            self.canvas.config(cursor="target")
            self.lbl_mode_status.config(
                text="MODE: 📍 PIN MODE ACTIVE — CLICK ANYWHERE ON 3D BODY TO ATTACH ISSUE",
                fg=ACCENT_YELLOW
            )
        else:
            self.btn_pin_mode.config(
                text="📍 PIN ON 3D BODY",
                bg="#b45309", fg="#fef3c7", highlightbackground="#f59e0b"
            )
            self.canvas.config(cursor="crosshair")
            if self.vr_mode:
                self.lbl_mode_status.config(
                    text="MODE: 🥽 VR STEREOSCOPIC 3D (DUAL-VIEWPORT ACTIVE)",
                    fg="#a5b4fc"
                )
            else:
                self.lbl_mode_status.config(
                    text="MODE: 📡 AR HOLOGRAPHIC HUD ACTIVE",
                    fg=ACCENT_GREEN
                )

    def _pick_issue_at_screen_pos(self, click_x: int, click_y: int) -> None:
        """Detects if user clicked directly on a 3D clinical issue marker pin."""
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 10 or h < 10:
            return

        coords = np.array([issue.coord_3d for issue in self.active_issues])
        sx, sy, _ = self.camera.project_points(coords, w, h)

        for i, issue in enumerate(self.active_issues):
            dist = math.hypot(click_x - sx[i], click_y - sy[i])
            if dist <= 18:  # 18px click radius
                self.selected_issue = issue
                self._update_diagnostic_card(issue)
                # Select in treeview
                self.issues_tree.selection_set(issue.id)
                self.issues_tree.see(issue.id)
                break

    def _open_add_issue_dialog(self, prefill_coord: Optional[np.ndarray] = None) -> None:
        """Dialog allowing user to add a custom clinical issue to 3D anatomy at runtime."""
        dlg = tk.Toplevel(self.root)
        dlg.title("Add Custom Clinical Pathology")
        dlg.geometry("440x490")
        dlg.configure(bg=PANEL_BG)
        dlg.grab_set()

        tk.Label(
            dlg, text="ADD CLINICAL PATHOLOGY / ISSUE",
            bg=PANEL_BG, fg=ACCENT_CYAN, font=("Segoe UI", 11, "bold")
        ).pack(pady=(10, 4))

        if prefill_coord is not None:
            tk.Label(
                dlg,
                text=f"📍 3D Surface Location: ({prefill_coord[0]:.2f}, {prefill_coord[1]:.2f}, {prefill_coord[2]:.2f})",
                bg=PANEL_BG, fg=ACCENT_YELLOW, font=("Consolas", 8, "bold")
            ).pack(pady=(0, 6))

        # Name Entry (Clean and empty for user entry)
        tk.Label(dlg, text="Pathology Name *:", bg=PANEL_BG, fg=TEXT_PRIMARY, font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=20)
        ent_name = tk.Entry(dlg, bg=PANEL_ALT_BG, fg=TEXT_PRIMARY, insertbackground="white", relief=tk.FLAT)
        ent_name.pack(fill=tk.X, padx=20, pady=(0, 8))
        ent_name.focus_set()  # Focus immediately so user can type

        # System Dropdown
        tk.Label(dlg, text="Anatomical System:", bg=PANEL_BG, fg=TEXT_PRIMARY, font=("Segoe UI", 9)).pack(anchor="w", padx=20)
        cbo_sys = ttk.Combobox(dlg, values=["Skeletal", "Circulatory", "Muscular", "Visceral"], state="readonly")
        cbo_sys.set("Skeletal" if (prefill_coord is not None and prefill_coord[1] < 0) else "Circulatory")
        cbo_sys.pack(fill=tk.X, padx=20, pady=(0, 8))

        # Severity Dropdown
        tk.Label(dlg, text="Severity Level:", bg=PANEL_BG, fg=TEXT_PRIMARY, font=("Segoe UI", 9)).pack(anchor="w", padx=20)
        cbo_sev = ttk.Combobox(dlg, values=["CRITICAL", "HIGH", "MODERATE"], state="readonly")
        cbo_sev.set("HIGH")
        cbo_sev.pack(fill=tk.X, padx=20, pady=(0, 8))

        # ICD-10 Entry (Empty by default)
        tk.Label(dlg, text="ICD-10 Diagnosis Code (Optional):", bg=PANEL_BG, fg=TEXT_PRIMARY, font=("Segoe UI", 9)).pack(anchor="w", padx=20)
        ent_icd = tk.Entry(dlg, bg=PANEL_ALT_BG, fg=TEXT_PRIMARY, insertbackground="white", relief=tk.FLAT)
        ent_icd.pack(fill=tk.X, padx=20, pady=(0, 8))

        # Clinical Description (Empty by default)
        tk.Label(dlg, text="Clinical Symptoms & Presentation (Optional):", bg=PANEL_BG, fg=TEXT_PRIMARY, font=("Segoe UI", 9)).pack(anchor="w", padx=20)
        ent_symp = tk.Entry(dlg, bg=PANEL_ALT_BG, fg=TEXT_PRIMARY, insertbackground="white", relief=tk.FLAT)
        ent_symp.pack(fill=tk.X, padx=20, pady=(0, 8))

        # Intervention Notes (Empty by default)
        tk.Label(dlg, text="AR Surgical / Intervention Plan (Optional):", bg=PANEL_BG, fg=TEXT_PRIMARY, font=("Segoe UI", 9)).pack(anchor="w", padx=20)
        ent_plan = tk.Entry(dlg, bg=PANEL_ALT_BG, fg=TEXT_PRIMARY, insertbackground="white", relief=tk.FLAT)
        ent_plan.pack(fill=tk.X, padx=20, pady=(0, 14))

        def _save_new_issue():
            name = ent_name.get().strip()
            if not name:
                messagebox.showerror("Required Field", "Please enter a Pathology Name.", parent=dlg)
                return
            new_id = f"ISS-{len(self.active_issues)+1:02d}"

            if prefill_coord is not None:
                rx, ry, rz = float(prefill_coord[0]), float(prefill_coord[1]), float(prefill_coord[2])
            else:
                # Randomize anchor near center chest/torso
                rx = float(np.random.uniform(-0.35, 0.35))
                ry = float(np.random.uniform(0.5, 1.8))
                rz = float(np.random.uniform(0.1, 0.3))

            icd_val = ent_icd.get().strip() or "R69 - Unspecified Pathology"
            symp_val = ent_symp.get().strip() or "Identified during 3D anatomical examination."
            plan_val = ent_plan.get().strip() or "Diagnostic imaging and clinical monitoring recommended."

            new_issue = ClinicalIssue(
                id=new_id,
                name=name,
                system=cbo_sys.get(),
                severity=cbo_sev.get(),
                coord_3d=np.array([rx, ry, rz]),
                icd10=icd_val,
                symptoms=symp_val,
                intervention=plan_val
            )
            self.active_issues.append(new_issue)
            self._refresh_issues_tree()
            self.selected_issue = new_issue
            self._update_diagnostic_card(new_issue)
            dlg.destroy()

        tk.Button(
            dlg, text="✓ ATTACH TO 3D ANATOMY",
            command=_save_new_issue,
            bg="#065f46", fg="#6ee7b7", relief=tk.FLAT, pady=6,
            font=("Segoe UI", 9, "bold"), cursor="hand2"
        ).pack(fill=tk.X, padx=20)

    # ═══════════════════════════════════════════
    # JSON CASE IMPORT & EXPORT (RUNTIME DATA)
    # ═══════════════════════════════════════════
    def _load_case_json(self) -> None:
        """Loads clinical issues dynamically from an external JSON file at runtime."""
        path = filedialog.askopenfilename(
            title="Load Clinical Case Record (JSON)",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        if not path:
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            raw_issues = data.get("issues", data if isinstance(data, list) else [])
            loaded = []
            for item in raw_issues:
                c = item.get("coord_3d", [0.0, 1.0, 0.2])
                loaded.append(ClinicalIssue(
                    id=item.get("id", f"ISS-{len(loaded)+1:02d}"),
                    name=item.get("name", "Unknown Issue"),
                    system=item.get("system", "Skeletal"),
                    severity=item.get("severity", "HIGH"),
                    coord_3d=np.array([float(c[0]), float(c[1]), float(c[2])]),
                    icd10=item.get("icd10", "R69"),
                    symptoms=item.get("symptoms", "Clinical presentation noted."),
                    intervention=item.get("intervention", "Medical/Surgical management plan.")
                ))

            if not loaded:
                messagebox.showwarning("Empty File", "No clinical issues found in this JSON file.")
                return

            self.active_issues = loaded
            self._refresh_issues_tree()
            self.selected_issue = self.active_issues[0]
            self._update_diagnostic_card(self.selected_issue)

            case_title = data.get("case_title", os.path.basename(path)) if isinstance(data, dict) else os.path.basename(path)
            messagebox.showinfo("Case Loaded Successfully", f"Loaded {len(loaded)} clinical issues for:\n'{case_title}'")
        except Exception as exc:
            messagebox.showerror("Error Loading JSON", f"Failed to parse case file:\n{exc}")

    def _save_case_json(self) -> None:
        """Exports all active clinical issues to a portable JSON file at runtime."""
        path = filedialog.asksaveasfilename(
            title="Export Case Record (JSON)",
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        if not path:
            return

        try:
            export_list = []
            for iss in self.active_issues:
                export_list.append({
                    "id": iss.id,
                    "name": iss.name,
                    "system": iss.system,
                    "severity": iss.severity,
                    "coord_3d": [float(iss.coord_3d[0]), float(iss.coord_3d[1]), float(iss.coord_3d[2])],
                    "icd10": iss.icd10,
                    "symptoms": iss.symptoms,
                    "intervention": iss.intervention
                })

            payload = {
                "case_title": "AR/VR Patient Clinical Record",
                "export_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_issues": len(export_list),
                "issues": export_list
            }

            with open(path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)

            messagebox.showinfo("Case Exported", f"Successfully saved {len(export_list)} issues to:\n{os.path.basename(path)}")
        except Exception as exc:
            messagebox.showerror("Error Saving JSON", f"Failed to export case file:\n{exc}")

    # ═══════════════════════════════════════════
    # 3D RENDERING PIPELINE (AR & VR MODES)
    # ═══════════════════════════════════════════
    def _render_frame(self) -> None:
        """Executes the complete 3D rendering pass and schedules next frame."""
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()

        if w > 10 and h > 10:
            if self.vr_mode:
                # 🥽 Dual-Viewport VR Stereoscopic Rendering
                half_w = w / 2.0
                # Left Eye (Negative parallax angle)
                self._render_single_viewport(
                    x_min=0, y_min=0, width=half_w, height=h,
                    eye_offset=-self.camera.stereo_ipd, eye_label="LEFT EYE [OS]"
                )
                # Right Eye (Positive parallax angle)
                self._render_single_viewport(
                    x_min=half_w, y_min=0, width=half_w, height=h,
                    eye_offset=self.camera.stereo_ipd, eye_label="RIGHT EYE [OD]"
                )
                # Divider between eyes
                self.canvas.create_line(half_w, 0, half_w, h, fill="#312e81", width=2)
            else:
                # 📡 Single-Viewport AR Holographic HUD Rendering
                self._render_single_viewport(
                    x_min=0, y_min=0, width=w, height=h,
                    eye_offset=0.0, eye_label="AR VIEWPORT"
                )
                self._draw_ar_hud_decorations(w, h)

        # Update telemetry text
        yaw_deg = math.degrees(self.camera.yaw) % 360
        pitch_deg = math.degrees(self.camera.pitch)
        layers_count = sum([self.show_skeletal.get(), self.show_circulatory.get(),
                            self.show_muscular.get(), self.show_visceral.get()])
        self.lbl_telemetry.config(
            text=f"YAW: {yaw_deg:.1f}° | PITCH: {pitch_deg:.1f}° | ZOOM: {int(self.camera.zoom)}% | LAYERS: {layers_count}/4"
        )

        self.root.after(30, self._render_frame)

    def _render_single_viewport(self, x_min: float, y_min: float, width: float,
                                height: float, eye_offset: float, eye_label: str) -> None:
        """Renders 3D anatomical layers, ground grid, and clinical issue pins for a specific eye."""

        # ── 1. Holographic Ground Grid Plane (Floor) ──
        if self.show_ground_grid.get():
            self._draw_3d_ground_grid(x_min, width, height, eye_offset)

        # ── 2. Collect Active Layer Geometry Elements ──
        active_elements = []
        if self.show_skeletal.get():
            active_elements.extend(self.geom_skeletal)
        if self.show_circulatory.get():
            active_elements.extend(self.geom_circulatory)
        if self.show_muscular.get():
            active_elements.extend(self.geom_muscular)
        if self.show_visceral.get():
            active_elements.extend(self.geom_visceral)

        # ── 3. Render Anatomical Lines and Loops ──
        for elem in active_elements:
            pts = elem["pts"]
            sx, sy, z_cam = self.camera.project_points(pts, width, height, eye_offset)
            # Offset to viewport bounds
            sx = sx + x_min

            col = elem["color"]
            w_line = elem.get("width", 1)

            # Painter's shading: slightly dimmer if farther back in depth
            avg_z = np.mean(z_cam)
            if avg_z < -0.3:
                w_line = max(1, w_line - 1)

            if elem["type"] == "line":
                coords = []
                for x, y in zip(sx, sy):
                    coords.extend([x, y])
                if len(coords) >= 4:
                    self.canvas.create_line(*coords, fill=col, width=w_line, smooth=True)

            elif elem["type"] == "loop":
                coords = []
                for x, y in zip(sx, sy):
                    coords.extend([x, y])
                if len(coords) >= 4:
                    coords.extend([coords[0], coords[1]])  # Close loop
                    self.canvas.create_line(*coords, fill=col, width=w_line, smooth=True)

        # ── 4. Render Clinical Diagnostic Issue Pins (3D Billboards) ──
        issue_coords = np.array([issue.coord_3d for issue in self.active_issues])
        if len(issue_coords) > 0:
            isx, isy, iz = self.camera.project_points(issue_coords, width, height, eye_offset)
            isx = isx + x_min

            # Sort issues by depth so nearest render on top
            depth_indices = np.argsort(iz)

            for idx in depth_indices:
                issue = self.active_issues[idx]
                px, py = isx[idx], isy[idx]
                is_selected = (self.selected_issue and self.selected_issue.id == issue.id)
                col = issue.severity_color

                # Outer pulse ring
                r_pulse = 9 if not is_selected else 13
                self.canvas.create_oval(
                    px - r_pulse, py - r_pulse, px + r_pulse, py + r_pulse,
                    outline=col, width=1, dash=(3, 2)
                )

                # Solid central marker
                r_core = 5 if not is_selected else 7
                self.canvas.create_oval(
                    px - r_core, py - r_core, px + r_core, py + r_core,
                    fill=col, outline="white", width=1
                )

                # Floating 3D Issue Label Callout
                label_text = f"[{issue.severity[0]}] {issue.name.split('(')[0].strip()}"
                self.canvas.create_line(px + r_pulse, py, px + r_pulse + 18, py - 12, fill=col, width=1)
                self.canvas.create_line(px + r_pulse + 18, py - 12, px + r_pulse + 95, py - 12, fill=col, width=1)

                self.canvas.create_text(
                    px + r_pulse + 22, py - 20, anchor="w",
                    text=label_text, fill=col, font=("Segoe UI", 7, "bold")
                )

        # ── 5. VR Lens Barrel Simulation Overlay ──
        if self.vr_mode:
            # Vignette border for VR goggle lens
            lens_r = min(width, height) * 0.48
            cx = x_min + width / 2.0
            cy = height / 2.0
            self.canvas.create_oval(
                cx - lens_r, cy - lens_r, cx + lens_r, cy + lens_r,
                outline="#4338ca", width=2, dash=(6, 4)
            )
            # Eye indicator
            self.canvas.create_text(
                x_min + 14, 18, anchor="nw",
                text=eye_label, fill="#818cf8", font=("Consolas", 9, "bold")
            )

    def _draw_3d_ground_grid(self, x_min: float, width: float, height: float, eye_offset: float) -> None:
        """Draws a 3D perspective holographic coordinate grid beneath the human body."""
        grid_y = -3.1  # Placed just below the feet
        grid_lines = []

        # Lines parallel to X-axis
        for z in np.linspace(-1.5, 1.5, 9):
            pts = np.linspace([-1.8, grid_y, z], [1.8, grid_y, z], 10)
            grid_lines.append(pts)

        # Lines parallel to Z-axis
        for x in np.linspace(-1.8, 1.8, 9):
            pts = np.linspace([x, grid_y, -1.5], [x, grid_y, 1.5], 10)
            grid_lines.append(pts)

        for line_pts in grid_lines:
            sx, sy, _ = self.camera.project_points(line_pts, width, height, eye_offset)
            sx = sx + x_min
            coords = []
            for x, y in zip(sx, sy):
                coords.extend([x, y])
            if len(coords) >= 4:
                self.canvas.create_line(*coords, fill=COLOR_GRID, width=1)

    def _draw_ar_hud_decorations(self, w: float, h: float) -> None:
        """Renders futuristic AR HUD brackets, scan reticle, and telemetry callouts."""
        corner = 28
        col = ACCENT_CYAN

        # Four Corner AR Brackets
        self.canvas.create_line(15, 15 + corner, 15, 15, 15 + corner, 15, fill=col, width=2)
        self.canvas.create_line(w - 15 - corner, 15, w - 15, 15, w - 15, 15 + corner, fill=col, width=2)
        self.canvas.create_line(15, h - 15 - corner, 15, h - 15, 15 + corner, h - 15, fill=col, width=2)
        self.canvas.create_line(w - 15 - corner, h - 15, w - 15, h - 15, w - 15, h - 15 - corner, fill=col, width=2)

        # Central AR Targeting Reticle (Subtle)
        cx, cy = w / 2.0, h / 2.0
        self.canvas.create_line(cx - 16, cy, cx - 6, cy, fill="#1e293b", width=1)
        self.canvas.create_line(cx + 6, cy, cx + 16, cy, fill="#1e293b", width=1)
        self.canvas.create_line(cx, cy - 16, cx, cy - 6, fill="#1e293b", width=1)
        self.canvas.create_line(cx, cy + 6, cx, cy + 16, fill="#1e293b", width=1)

        # AR Status Text
        self.canvas.create_text(
            22, 22, anchor="nw",
            text="HOLO-OPTIC V&AR ENGINE v4.2\nPATIENT: ADULT ANATOMY MODEL\nTRACKING: SPATIAL 6-DOF ANCHOR",
            fill=ACCENT_CYAN, font=("Consolas", 8)
        )

    # ═══════════════════════════════════════════
    # SNAPSHOT EXPORT
    # ═══════════════════════════════════════════
    def _export_snapshot(self) -> None:
        """Exports the current 3D viewport canvas as a high-resolution PNG image."""
        save_path = filedialog.asksaveasfilename(
            title="Export AR/VR Viewport Snapshot",
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png"), ("JPEG Image", "*.jpg"), ("All Files", "*.*")]
        )
        if not save_path:
            return

        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        img = Image.new("RGB", (w, h), CANVAS_BG)
        draw = ImageDraw.Draw(img)

        # Render active layer lines onto PIL Image
        active_elements = []
        if self.show_skeletal.get():
            active_elements.extend(self.geom_skeletal)
        if self.show_circulatory.get():
            active_elements.extend(self.geom_circulatory)
        if self.show_muscular.get():
            active_elements.extend(self.geom_muscular)
        if self.show_visceral.get():
            active_elements.extend(self.geom_visceral)

        for elem in active_elements:
            sx, sy, _ = self.camera.project_points(elem["pts"], w, h)
            col = elem["color"]
            coords = [(x, y) for x, y in zip(sx, sy)]
            if len(coords) >= 2:
                draw.line(coords, fill=col, width=elem.get("width", 1))

        # Render issue pins
        issue_coords = np.array([issue.coord_3d for issue in self.active_issues])
        if len(issue_coords) > 0:
            isx, isy, _ = self.camera.project_points(issue_coords, w, h)
            for i, issue in enumerate(self.active_issues):
                px, py = isx[i], isy[i]
                draw.ellipse([px - 5, py - 5, px + 5, py + 5], fill=issue.severity_color, outline="white")
                draw.text((px + 10, py - 8), f"[{issue.severity[0]}] {issue.name}", fill=issue.severity_color)

        img.save(save_path)
        messagebox.showinfo("Export Successful", f"AR/VR Snapshot saved successfully to:\n{save_path}")


# ─────────────────────────────────────────────────────────────────────────────
# 7. MAIN RUNNER ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────
def main() -> None:
    """Initializes and runs the BioVision 3D application."""
    root = tk.Tk()
    app = BioVision3DApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
