# BioVision 3D — Holographic AR/VR Medical Anatomy & Clinical Pathology Visualizer

An interactive 3D Virtual & Augmented Reality (V&AR) application for real-time anatomical layer exploration, surgical planning, and clinical pathology annotation.

---

## 🚀 Quick Start — How to Run

### 1. Open Terminal in Project Directory
```powershell
cd "d:\aih assn6"
```

### 2. Install Dependencies
```powershell
pip install numpy Pillow
```

### 3. Launch the Application
```powershell
python medical_image_labeler.py
```

---

## ⚡ Runtime Issue Management (Zero Hardcoding)

You can add, edit, load, save, and delete clinical issues completely at **runtime** without modifying any code:

### 1. 📍 Direct 3D Surface Pinning (Click-to-Place)
1. Click **`📍 PIN ON 3D BODY`** in the top toolbar.
2. The cursor changes to a targeting reticle. Click anywhere on the 3D anatomical model (e.g., knee, chest, head, liver, arm).
3. The app executes an inverse raycast to calculate the exact 3D spatial coordinate $(X, Y, Z)$ and opens the clinical form.
4. Enter the pathology name, severity level, and symptoms, and click **`✓ ATTACH TO 3D ANATOMY`**.
5. The issue pin is instantly anchored onto that 3D location and rotates with the model in real time!

### 2. 📂 Runtime JSON Case Loading (`LOAD CASE (JSON)`)
- Click **`📂 LOAD CASE (JSON)`** to import external patient records on the fly.
- Two pre-configured clinical case files are provided in the folder for demonstration:
  - [`case_polytrauma_patient.json`](case_polytrauma_patient.json) — High-velocity road accident trauma patient.
  - [`case_cardiology_patient.json`](case_cardiology_patient.json) — Cardiac Care Unit (CCU) cardiovascular patient.

### 3. 💾 Runtime JSON Case Export (`SAVE CASE (JSON)`)
- Click **`💾 SAVE CASE (JSON)`** to export all active issues (including newly placed ones) to a portable `.json` file for persistence and sharing.

### 4. ➕ Manual Issue Form (`ADD ISSUE`)
- Click **`➕ ADD ISSUE`** to add a case via a clinical entry dialog with ICD-10 diagnosis codes and surgical intervention notes.

### 5. 🗑 Runtime Issue Deletion
- Select any issue from the sidebar list or click its 3D marker on the body, then click **`🗑 DELETE ISSUE`**.

---

## 🌟 Key Features & V&AR Architecture

### 1. True 3D Parametric Human Anatomy (No Stickman)
- **High-Fidelity 3D Anatomical Contours:** Sculpted skull/cranium with facial orbits, natural S-curved vertebral column, 10 paired 3D curved ribcage arches, clavicles, scapulae, pelvic girdle, femurs, tibias, fibulas, and limb bones.
- **360° Real-Time 3D Interaction:**
  - **Left-Click + Drag:** Orbit around the human body in 360° (Yaw & Pitch).
  - **Right-Click + Drag:** Pan camera horizontally/vertically.
  - **Mouse Wheel:** Zoom in/out to inspect fine structures.
  - **Auto-Orbit Button:** Automated holographic turntable showcase rotation.

---

### 2. Four Overlapping Anatomical Layers (Multi-Layer Stacking)
Toggle and overlap any combination of layers simultaneously to simulate medical AR/VR overlays (e.g., Microsoft HoloLens, BioDigital Human):
- 🦴 **Skeletal Layer:** Bones, cranium vault, spine, rib arches, pelvis, and limbs.
- 🫀 **Circulatory Layer:** 3D heart chamber, ascending/descending aorta, carotids, vena cava, and peripheral vascular networks.
- 💪 **Muscular Layer:** Volumetric muscle envelopes (pectoralis, deltoids, biceps, 6-pack rectus abdominis, quadriceps, calf muscles).
- 🧠 **Visceral / Organs Layer:** Left/Right lung volumes, liver wedge, J-shaped stomach, kidneys, and brain hemispheres.

---

### 3. Clinical Pathology & Diagnostic Issues (NOT Body Parts)
Anchored in 3D space with genuine ICD-10 diagnostic coding, severity triage, and AR surgical navigation:
- 🔴 **CRITICAL:** Myocardial Infarction, Aortic Aneurysm, Tension Pneumothorax, Skull Fracture & Epidural Bleed.
- 🟠 **HIGH:** Displaced Femur Fracture, Hepatic Lesion, Deep Vein Thrombosis.
- 🟡 **MODERATE:** Lumbar Disc Herniation, Distal Biceps Rupture, Rectus Femoris Tear.

---

### 4. Dual Reality Modes: AR vs. VR
- 📡 **AR Holographic HUD Mode (Augmented Reality):**
  - Single high-tech viewport with coordinate ground grid, corner brackets, telemetry readouts, and floating 3D billboarding issue pins.
- 🥽 **VR Stereoscopic 3D Mode (Virtual Reality):**
  - Dual side-by-side viewport (**Left Eye** and **Right Eye**) with authentic binocular parallax ($\pm \Delta \theta$ IPD optical separation).
  - Simulated circular VR lens barrels/vignettes (mimicking Meta Quest 3 / Apple Vision Pro).
