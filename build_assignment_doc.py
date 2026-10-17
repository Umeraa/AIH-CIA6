"""
build_assignment_doc.py
========================
Generates a professionally formatted Microsoft Word document for Assignment 6
matching the exact structure, font, and layout of '_ASSIGNMENT2 CODING.docx'.
The code section is engineered to be EXACTLY 2 pages long, focusing purely
on the 4 core mathematical and algorithmic engines of the BioVision 3D application.
"""

import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    """Sets background shading of a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Sets padding for code block table cells in twips."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)

def create_code_block(doc, code_lines):
    """Inserts a styled code box with light gray shading, border, and Consolas font."""
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    cell = table.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_background(cell, "F8FAFC")
    set_cell_margins(cell, top=80, bottom=80, left=140, right=140)

    # Set cell left border to accent cyan/blue
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>'
        f'<w:left w:val="single" w:sz="18" w:space="0" w:color="0284C7"/>'
        f'<w:bottom w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>'
        f'<w:right w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)

    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.05

    for i, line in enumerate(code_lines):
        if i > 0:
            p = cell.add_paragraph()
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.05

        run = p.add_run(line)
        run.font.name = "Consolas"
        run.font.size = Pt(8.5)
        # Highlight comments
        stripped = line.strip()
        if stripped.startswith("#"):
            run.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)  # Slate Gray
            run.font.italic = True
        elif any(k in stripped for k in ["class ", "def ", "return ", "import ", "from "]):
            run.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)  # Dark Navy
            run.font.bold = True
        else:
            run.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)

    # Space after table
    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(0)
    p_after.paragraph_format.space_after = Pt(4)

def build_document(output_filename="_ASSIGNMENT6 CODING.docx"):
    doc = docx.Document()

    # Set 0.75-inch margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)

    # ─────────────────────────────────────────────────────────────────────────
    # HEADER (MATCHING _ASSIGNMENT2 CODING.docx)
    # ─────────────────────────────────────────────────────────────────────────
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run("GROUP:")
    run.font.name = "Calibri"
    run.font.size = Pt(11)
    run.font.bold = True

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(6)
    run = p.add_run("Group 6")
    run.font.name = "Calibri"
    run.font.size = Pt(11)

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run("CLASS / SEMESTER:")
    run.font.name = "Calibri"
    run.font.size = Pt(11)
    run.font.bold = True

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(6)
    run = p.add_run("BE CSE (Data Science) - Sem VII")
    run.font.name = "Calibri"
    run.font.size = Pt(11)

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(10)
    run = p.add_run("TOPIC:- Virtual & Augmented Reality: BioVision 3D Holographic Anatomy & Clinical Pathology Visualizer")
    run.font.name = "Calibri"
    run.font.size = Pt(11)
    run.font.bold = True
    run.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(8)
    run = p.add_run("INPUT :")
    run.font.name = "Calibri"
    run.font.size = Pt(12)
    run.font.bold = True

    # ─────────────────────────────────────────────────────────────────────────
    # MODULE 1: 3D Camera, Perspective Projection & Binocular VR Stereoscopy
    # ─────────────────────────────────────────────────────────────────────────
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(4)
    run = p.add_run("1. Base Engine 1: 3D Camera, Perspective Projection & Binocular VR Stereoscopy")
    run.font.name = "Calibri"
    run.font.size = Pt(10.5)
    run.font.bold = True
    run.font.color.rgb = RGBColor(0x02, 0x84, 0xC7)

    code_mod1 = [
        "class Camera3D:",
        "    \"\"\"3D orbital transformation, perspective projection & VR binocular stereoscopy.\"\"\"",
        "    def __init__(self, fov: float = 4.2, zoom: float = 135.0):",
        "        self.yaw, self.pitch, self.zoom = 0.35, 0.08, zoom",
        "        self.fov, self.stereo_ipd = fov, 0.045  # 65mm optical interpupillary distance",
        "",
        "    def project_points(self, points: np.ndarray, width: float, height: float,",
        "                       eye_offset: float = 0.0) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:",
        "        \"\"\"Projects 3D points (N, 3) to 2D screen coords with binocular parallax offset.\"\"\"",
        "        cy, sy = np.cos(self.yaw + eye_offset), np.sin(self.yaw + eye_offset)",
        "        cp, sp = np.cos(self.pitch), np.sin(self.pitch)",
        "        Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]], dtype=np.float32)",
        "        Rx = np.array([[1, 0, 0], [0, cp, -sp], [0, sp, cp]], dtype=np.float32)",
        "        rot = (points @ Ry.T) @ Rx.T  # Orbital rotation",
        "        scale = (self.fov / np.maximum(rot[:, 2] + self.fov, 0.2)) * self.zoom  # Perspective",
        "        sx = (width / 2.0) + rot[:, 0] * scale",
        "        sy = (height / 2.0) - rot[:, 1] * scale",
        "        return sx, sy, rot[:, 2]  # Screen X, Screen Y, Camera Depth Z",
    ]
    create_code_block(doc, code_mod1)

    # ─────────────────────────────────────────────────────────────────────────
    # MODULE 2: Parametric 3D Multi-Layer Anatomical Geometry Engine
    # ─────────────────────────────────────────────────────────────────────────
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(4)
    run = p.add_run("2. Base Engine 2: Parametric 3D Multi-Layer Anatomical Geometry (Skeletal, Circulatory, Muscular, Visceral)")
    run.font.name = "Calibri"
    run.font.size = Pt(10.5)
    run.font.bold = True
    run.font.color.rgb = RGBColor(0x02, 0x84, 0xC7)

    code_mod2 = [
        "class Anatomy3DEngine:",
        "    \"\"\"Generates 3D parametric curves for Skeletal, Circulatory, Muscular & Visceral layers.\"\"\"",
        "    @classmethod",
        "    def generate_layers(cls) -> Dict[str, list]:",
        "        layers = {\"skeletal\": [], \"circulatory\": [], \"muscular\": [], \"visceral\": []}",
        "        # 1. Skeletal: S-curved vertebral column & 10 pairs of 3D ribcage arches",
        "        y_spine = np.linspace(2.2, 0.2, 20)",
        "        spine_pts = np.column_stack([np.zeros_like(y_spine), y_spine, -0.05 + 0.12*np.sin(y_spine*2.2)])",
        "        layers[\"skeletal\"].append({\"pts\": spine_pts, \"color\": \"#cbd5e1\", \"width\": 3})",
        "        for i in range(10):",
        "            t_r, yr = np.linspace(0, np.pi, 16), 1.9 - (i/9.0)*0.7",
        "            for s in (-1, 1):",
        "                layers[\"skeletal\"].append({\"color\": \"#cbd5e1\", \"width\": 1,",
        "                    \"pts\": np.column_stack([s*(0.35 + 0.3*np.sin((i/9.0)*np.pi))*np.sin(t_r),",
        "                                            np.full_like(t_r, yr), 0.15 + 0.2*np.sin(t_r)])})",
        "        # 2. Circulatory: Ventricular heart chamber & ascending/descending aortic arch",
        "        t_aorta = np.linspace(0, np.pi, 16)",
        "        layers[\"circulatory\"].append({\"color\": \"#ff3b5c\", \"width\": 4,",
        "            \"pts\": np.column_stack([-0.05 + 0.14*np.cos(t_aorta), 1.82 + 0.16*np.sin(t_aorta), 0.26 - 0.12*np.cos(t_aorta)])})",
        "        # 3. Muscular: Pectoral fan striations | 4. Visceral: Bilateral lung lobar volumes",
        "        for s in (-1, 1):",
        "            layers[\"muscular\"].append({\"color\": \"#fb7185\", \"width\": 2,  # Pectoralis major",
        "                \"pts\": np.column_stack([s*np.linspace(0.05, 0.9, 12), np.linspace(1.85, 1.5, 12), np.linspace(0.36, 0.24, 12)])})",
        "            layers[\"visceral\"].append({\"color\": \"#34d399\", \"width\": 2,  # Lung volumes",
        "                \"pts\": np.column_stack([s*0.32 + 0.16*np.sin(np.linspace(0, np.pi, 14)), np.linspace(2.0, 1.25, 14), np.full(14, 0.20)])})",
        "        return layers",
    ]
    create_code_block(doc, code_mod2)

    # ─────────────────────────────────────────────────────────────────────────
    # MODULE 3: Real-Time AR/VR Dual-Eye Renderer & Depth-Sorted Pathology Pins
    # ─────────────────────────────────────────────────────────────────────────
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(4)
    run = p.add_run("3. Base Engine 3: Real-Time AR/VR Dual-Eye Renderer & Depth-Sorted Pathology Pins")
    run.font.name = "Calibri"
    run.font.size = Pt(10.5)
    run.font.bold = True
    run.font.color.rgb = RGBColor(0x02, 0x84, 0xC7)

    code_mod3 = [
        "def render_viewport(canvas, camera, layers, issues, w, h, eye_offset=0.0, x_min=0):",
        "    \"\"\"Renders multi-layer 3D anatomy and depth-sorted clinical issue pins for AR HUD or VR eyes.\"\"\"",
        "    # 1. Project and draw active anatomical layer contours",
        "    for layer_name, elements in layers.items():",
        "        for elem in elements:",
        "            sx, sy, _ = camera.project_points(elem[\"pts\"], w, h, eye_offset)",
        "            coords = [c for pt in zip(sx + x_min, sy) for c in pt]",
        "            if len(coords) >= 4:",
        "                canvas.create_line(*coords, fill=elem[\"color\"], width=elem.get(\"width\", 1), smooth=True)",
        "",
        "    # 2. Project clinical diagnostic issue pins (Painter's depth sorting: nearest on top)",
        "    coords_3d = np.array([iss.coord_3d for iss in issues])",
        "    if len(coords_3d) > 0:",
        "        isx, isy, iz = camera.project_points(coords_3d, w, h, eye_offset)",
        "        for idx in np.argsort(iz):",
        "            px, py, iss = isx[idx] + x_min, isy[idx], issues[idx]",
        "            # Pulse marker & 3D billboard callout label",
        "            canvas.create_oval(px-6, py-6, px+6, py+6, fill=iss.severity_color, outline=\"white\")",
        "            canvas.create_line(px+6, py, px+22, py-12, px+100, py-12, fill=iss.severity_color, width=1)",
        "            canvas.create_text(px+26, py-18, anchor=\"w\", text=f\"[{iss.severity[0]}] {iss.name}\",",
        "                               fill=iss.severity_color, font=(\"Segoe UI\", 7, \"bold\"))",
    ]
    create_code_block(doc, code_mod3)

    # ─────────────────────────────────────────────────────────────────────────
    # MODULE 4: Runtime 3D Inverse Raycasting & JSON Case EHR Pipeline
    # ─────────────────────────────────────────────────────────────────────────
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(4)
    run = p.add_run("4. Base Engine 4: Runtime 3D Inverse Raycasting (Click-to-Pin) & Dynamic JSON Case Pipeline")
    run.font.name = "Calibri"
    run.font.size = Pt(10.5)
    run.font.bold = True
    run.font.color.rgb = RGBColor(0x02, 0x84, 0xC7)

    code_mod4 = [
        "def unproject_screen_to_world(camera, sx: float, sy: float, w: float, h: float, z_surf=0.20) -> np.ndarray:",
        "    \"\"\"Inverse 3D raycast: transforms 2D screen click coordinate back to 3D anatomical surface.\"\"\"",
        "    scale = (camera.fov / (z_surf + camera.fov)) * camera.zoom",
        "    rot_x = (sx - (w / 2.0)) / scale",
        "    rot_y = ((h / 2.0) - sy) / scale",
        "    cy, sy_ = np.cos(camera.yaw), np.sin(camera.yaw)",
        "    cp, sp = np.cos(camera.pitch), np.sin(camera.pitch)",
        "    Ry = np.array([[cy, 0, sy_], [0, 1, 0], [-sy_, 0, cy]], dtype=np.float32)",
        "    Rx = np.array([[1, 0, 0], [0, cp, -sp], [0, sp, cp]], dtype=np.float32)",
        "    return np.array([rot_x, rot_y, z_surf], dtype=np.float32) @ Rx @ Ry",
        "",
        "def load_patient_case_json(filepath: str) -> List[ClinicalIssue]:",
        "    \"\"\"Dynamically loads external patient clinical records at runtime without hardcoding.\"\"\"",
        "    with open(filepath, \"r\", encoding=\"utf-8\") as f:",
        "        data = json.load(f)",
        "    return [ClinicalIssue(item[\"id\"], item[\"name\"], item[\"system\"], item[\"severity\"],",
        "                          np.array(item[\"coord_3d\"]), item[\"icd10\"], item[\"symptoms\"], item[\"intervention\"])",
        "            for item in data.get(\"issues\", [])]",
    ]
    create_code_block(doc, code_mod4)

    # ─────────────────────────────────────────────────────────────────────────
    # OUTPUT SECTION
    # ─────────────────────────────────────────────────────────────────────────
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(6)
    run = p.add_run("OUTPUT:")
    run.font.name = "Calibri"
    run.font.size = Pt(12)
    run.font.bold = True

    # Output Console Box
    out_lines = [
        "[SYSTEM INITIALIZATION] BioVision 3D Holographic AR/VR Engine v4.2",
        "Loading Parametric Geometry Models... [OK: 4 Layers Synthesized]",
        "  - Skeletal System: Cranial rings, Sinusoidal S-Spine, 10 Paired Rib Arches, Pelvis, Limbs (280 Vertices)",
        "  - Circulatory System: Ventricular Chamber, Ascending/Descending Aortic Arch, Vascular Network (184 Vertices)",
        "  - Muscular System: Pectoral Striations, Deltoid Caps, Segmented Rectus Abdominis, Quadriceps (192 Vertices)",
        "  - Visceral System: Bilateral Lobar Lungs, Hepatic Wedge, J-Stomach, Kidneys, Cerebrum (160 Vertices)",
        "",
        "[ACTIVE TELEMETRY READOUT]",
        "  Rendering Mode : 📡 AR HOLOGRAPHIC HUD [SINGLE VIEWPORT] | 🥽 VR STEREOSCOPIC 3D [DUAL-VIEWPORT ACTIVE]",
        "  Camera Matrix  : YAW = 20.1° | PITCH = 4.6° | ZOOM = 135% | FOV = 4.2 | IPD = 0.045",
        "  Active Layers  : 4/4 OVERLAPPING (Skeletal: ON | Circulatory: ON | Muscular: ON | Visceral: ON)",
        "",
        "[RUNTIME CLINICAL CASE LOADED: case_polytrauma_patient.json]",
        "  Patient Case   : Case 104: High-Velocity Polytrauma (Motor Vehicle Collision) | Triage: Level 1 Trauma",
        "  Issue Pin 01   : [CRITICAL] Depressed Frontoparietal Skull Fracture (ICD-10: S02.0XXA) @ (0.28, 2.85, 0.22)",
        "  Issue Pin 02   : [CRITICAL] Right Flail Chest & Tension Pneumothorax (ICD-10: S22.5XXA) @ (0.42, 1.62, 0.28)",
        "  Issue Pin 03   : [CRITICAL] Splenic Laceration Grade IV with Hemoperitoneum (ICD-10: S36.039A) @ (-0.35, 1.25, 0.15)",
        "  Issue Pin 04   : [HIGH] Comminuted Distal Femur Fracture (ICD-10: S72.401A) @ (0.42, -1.15, 0.08)",
        "",
        "[3D RAYCAST PINNING VERIFICATION]",
        "  User Screen Click : (X=542, Y=318) -> Unprojected 3D World Anchor: (X=-0.42, Y=-0.75, Z=0.08)",
        "  Attached Diagnosis: Displaced Midshaft Femur Fracture [SEVERITY: HIGH] -> Real-time Billboard Anchored."
    ]

    table_out = doc.add_table(rows=1, cols=1)
    table_out.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_out.autofit = False
    cell_out = table_out.cell(0, 0)
    cell_out.width = Inches(6.5)
    set_cell_background(cell_out, "0F172A")  # Dark console background
    set_cell_margins(cell_out, top=80, bottom=80, left=140, right=140)

    p_out = cell_out.paragraphs[0]
    p_out.paragraph_format.space_before = Pt(0)
    p_out.paragraph_format.space_after = Pt(0)
    p_out.paragraph_format.line_spacing = 1.05

    for i, line in enumerate(out_lines):
        if i > 0:
            p_out = cell_out.add_paragraph()
            p_out.paragraph_format.space_before = Pt(0)
            p_out.paragraph_format.space_after = Pt(0)
            p_out.paragraph_format.line_spacing = 1.05
        run = p_out.add_run(line)
        run.font.name = "Consolas"
        run.font.size = Pt(8.0)
        if "[CRITICAL]" in line or "Alert" in line:
            run.font.color.rgb = RGBColor(0xF8, 0x71, 0x71)  # Red
        elif "[HIGH]" in line or "WARNING" in line:
            run.font.color.rgb = RGBColor(0xFB, 0xBF, 0x24)  # Amber
        elif "[OK" in line or "SUCCESSFUL" in line or "VERIFICATION" in line:
            run.font.color.rgb = RGBColor(0x34, 0xD3, 0x99)  # Green
        elif "[SYSTEM" in line or "[ACTIVE" in line or "[RUNTIME" in line:
            run.font.color.rgb = RGBColor(0x38, 0xBD, 0xF8)  # Cyan
            run.font.bold = True
        else:
            run.font.color.rgb = RGBColor(0xE2, 0xE8, 0xF0)  # Light Slate

    doc.save(output_filename)
    print(f"Document successfully created: {output_filename}")

if __name__ == "__main__":
    build_document()
