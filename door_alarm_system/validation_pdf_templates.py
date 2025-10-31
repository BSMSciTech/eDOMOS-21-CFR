"""
Simple PDF Templates for IQ/OQ/PQ Documentation
Generates pre-filled PDF forms that customers can print, fill, and sign manually
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from datetime import datetime
import io


def generate_iq_template_pdf(equipment_info, company_info, customer_info=None):
    """
    Generate Installation Qualification (IQ) PDF Template
    
    Args:
        equipment_info: dict with keys: name, model, serial, version
        company_info: dict with keys: company_name, address, email, phone
        customer_info: dict with keys: customer_name, site, department (optional)
    
    Returns:
        BytesIO buffer containing PDF
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                           rightMargin=0.75*inch, leftMargin=0.75*inch,
                           topMargin=1*inch, bottomMargin=0.75*inch)
    
    # Container for PDF elements
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1a472a'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2e7d32'),
        spaceAfter=10,
        spaceBefore=15,
        fontName='Helvetica-Bold'
    )
    
    # Title
    elements.append(Paragraph("INSTALLATION QUALIFICATION (IQ)", title_style))
    elements.append(Paragraph("Door Monitoring System - eDOMOS", styles['Heading3']))
    elements.append(Spacer(1, 0.3*inch))
    
    # Document Information Table
    doc_data = [
        ['Document Title:', 'Installation Qualification (IQ)'],
        ['Document No.:', f'IQ-{datetime.now().strftime("%Y-%m-%d-%H%M")}'],
        ['System Name:', equipment_info.get('name', 'eDOMOS Door Monitoring System')],
        ['Equipment Model:', equipment_info.get('model', 'eDOMOS-2.1-Pro')],
        ['Serial Number:', equipment_info.get('serial', '________________')],
        ['Software Version:', equipment_info.get('version', 'v2.1.0')],
        ['Date Prepared:', datetime.now().strftime('%Y-%m-%d')],
    ]
    
    doc_table = Table(doc_data, colWidths=[2.5*inch, 4*inch])
    doc_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f5e9')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(doc_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Manufacturer Information
    elements.append(Paragraph("1. MANUFACTURER / SUPPLIER INFORMATION", heading_style))
    mfg_data = [
        ['Company Name:', company_info.get('company_name', '________________')],
        ['Address:', company_info.get('address', '________________')],
        ['Contact Email:', company_info.get('email', '________________')],
        ['Contact Phone:', company_info.get('phone', '________________')],
    ]
    mfg_table = Table(mfg_data, colWidths=[2*inch, 4.5*inch])
    mfg_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(mfg_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Customer/Site Information
    elements.append(Paragraph("2. CUSTOMER / SITE INFORMATION", heading_style))
    if customer_info:
        cust_data = [
            ['Customer Name:', customer_info.get('customer_name', '________________')],
            ['Department:', customer_info.get('department', '________________')],
            ['Site Location:', customer_info.get('site', '________________')],
            ['Installation Date:', '________________'],
        ]
    else:
        cust_data = [
            ['Customer Name:', '________________'],
            ['Department:', '________________'],
            ['Site Location:', '________________'],
            ['Installation Date:', '________________'],
        ]
    
    cust_table = Table(cust_data, colWidths=[2*inch, 4.5*inch])
    cust_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(cust_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Purpose
    elements.append(Paragraph("3. PURPOSE", heading_style))
    purpose_text = """
    To verify and document that the installation of the Door Monitoring System (hardware and 
    software components) has been carried out in accordance with the approved design specifications 
    and manufacturer's installation procedures.
    """
    elements.append(Paragraph(purpose_text, styles['BodyText']))
    elements.append(Spacer(1, 0.2*inch))
    
    # Scope
    elements.append(Paragraph("4. SCOPE", heading_style))
    scope_text = f"""
    This IQ covers the installation of the eDOMOS Door Monitoring System at the customer site. 
    It includes verification of hardware components, software installation, network configuration, 
    and documentation for equipment serial number: {equipment_info.get('serial', 'N/A')}.
    """
    elements.append(Paragraph(scope_text, styles['BodyText']))
    elements.append(Spacer(1, 0.2*inch))
    
    # Hardware Verification Checklist
    elements.append(Paragraph("5. HARDWARE VERIFICATION", heading_style))
    hw_data = [
        ['Component', 'Make/Model', 'Serial No.', 'Installed\n(Y/N)', 'Verified By', 'Remarks'],
        ['Raspberry Pi Controller', '', '', '', '', ''],
        ['Magnetic Door Sensor', '', '', '', '', ''],
        ['Relay Module', '', '', '', '', ''],
        ['Hooter/Alarm', '', '', '', '', ''],
        ['Power Supply (5V/12V)', '', '', '', '', ''],
        ['Enclosure/Housing', '', '', '', '', ''],
        ['Network Cable/Wi-Fi', '', '', '', '', ''],
    ]
    
    hw_table = Table(hw_data, colWidths=[1.3*inch, 1*inch, 0.9*inch, 0.6*inch, 1*inch, 1.7*inch])
    hw_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e7d32')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(hw_table)
    elements.append(PageBreak())
    
    # Software Verification
    elements.append(Paragraph("6. SOFTWARE VERIFICATION", heading_style))
    sw_data = [
        ['Parameter', 'Expected Value', 'Actual Value', 'Verified\n(Y/N)', 'Remarks'],
        ['Software Version', equipment_info.get('version', 'v2.1.0'), '', '', ''],
        ['Database Configured', 'SQLite Installed', '', '', ''],
        ['User Access Control', 'Admin account created', '', '', ''],
        ['Audit Trail Enabled', 'Blockchain active', '', '', ''],
        ['Network Connectivity', 'LAN/Wi-Fi operational', '', '', ''],
        ['Event Logging', 'Logs saving to DB', '', '', ''],
    ]
    
    sw_table = Table(sw_data, colWidths=[1.8*inch, 1.5*inch, 1.3*inch, 0.7*inch, 2.2*inch])
    sw_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e7d32')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(sw_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Documentation Verification
    elements.append(Paragraph("7. DOCUMENTATION VERIFICATION", heading_style))
    doc_ver_data = [
        ['Document', 'Document No.', 'Verified\n(Y/N)', 'Remarks'],
        ['User Manual', '', '', ''],
        ['Installation Guide', '', '', ''],
        ['Wiring Diagram', '', '', ''],
        ['System Configuration Sheet', '', '', ''],
        ['Calibration Certificates', 'If applicable', '', ''],
    ]
    
    doc_ver_table = Table(doc_ver_data, colWidths=[2.2*inch, 1.8*inch, 0.8*inch, 2.7*inch])
    doc_ver_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e7d32')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(doc_ver_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Conclusion
    elements.append(Paragraph("8. CONCLUSION", heading_style))
    conclusion_text = """
    The installation of the Door Monitoring System has been completed and verified as per approved 
    procedures. All required hardware components are installed, software is configured, and documentation 
    is reviewed. The system is deemed ready for Operational Qualification (OQ).
    """
    elements.append(Paragraph(conclusion_text, styles['BodyText']))
    elements.append(Spacer(1, 0.3*inch))
    
    # Sign-off Section
    elements.append(Paragraph("9. SIGN-OFF", heading_style))
    signoff_data = [
        ['Role', 'Name', 'Signature', 'Date'],
        ['Prepared by\n(Installer/Engineer)', '', '', ''],
        ['Verified by\n(System Owner)', '', '', ''],
        ['Approved by\n(QA Representative)', '', '', ''],
    ]
    
    signoff_table = Table(signoff_data, colWidths=[2*inch, 1.8*inch, 1.8*inch, 1.9*inch])
    signoff_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e7d32')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    elements.append(signoff_table)
    
    # Footer note
    elements.append(Spacer(1, 0.3*inch))
    footer_text = """
    <i>Note: This is a template document. Print, complete manually, sign, and file as per your 
    organization's document control procedures. For FDA 21 CFR Part 11 compliance, use electronic 
    signatures through the eDOMOS web interface.</i>
    """
    elements.append(Paragraph(footer_text, styles['Italic']))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_oq_template_pdf(equipment_info, company_info):
    """Generate Operational Qualification (OQ) PDF Template"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                           rightMargin=0.75*inch, leftMargin=0.75*inch,
                           topMargin=1*inch, bottomMargin=0.75*inch)
    
    elements = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1565c0'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1976d2'),
        spaceAfter=10,
        spaceBefore=15,
        fontName='Helvetica-Bold'
    )
    
    # Title
    elements.append(Paragraph("OPERATIONAL QUALIFICATION (OQ)", title_style))
    elements.append(Paragraph("Door Monitoring System - eDOMOS", styles['Heading3']))
    elements.append(Spacer(1, 0.3*inch))
    
    # Document Header
    doc_data = [
        ['Document Title:', 'Operational Qualification (OQ)'],
        ['Document No.:', f'OQ-{datetime.now().strftime("%Y-%m-%d-%H%M")}'],
        ['System Name:', equipment_info.get('name', 'eDOMOS Door Monitoring System')],
        ['Equipment Model:', equipment_info.get('model', 'eDOMOS-2.1-Pro')],
        ['Serial Number:', equipment_info.get('serial', '________________')],
        ['Date Prepared:', datetime.now().strftime('%Y-%m-%d')],
    ]
    
    doc_table = Table(doc_data, colWidths=[2.5*inch, 4*inch])
    doc_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e3f2fd')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(doc_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Purpose
    elements.append(Paragraph("1. PURPOSE", heading_style))
    purpose_text = """
    To verify and document that all functions of the Door Monitoring System operate as designed 
    and meet the specified operational requirements under normal operating conditions.
    """
    elements.append(Paragraph(purpose_text, styles['BodyText']))
    elements.append(Spacer(1, 0.2*inch))
    
    # Scope
    elements.append(Paragraph("2. SCOPE", heading_style))
    scope_text = """
    This OQ covers functional testing of the eDOMOS Door Monitoring System including door sensor 
    detection, alarm triggering, event logging, user authentication, and real-time monitoring features.
    """
    elements.append(Paragraph(scope_text, styles['BodyText']))
    elements.append(Spacer(1, 0.2*inch))
    
    # Functional Tests
    elements.append(Paragraph("3. FUNCTIONAL TESTS", heading_style))
    func_data = [
        ['Test No.', 'Test Description', 'Expected Result', 'Actual Result', 'Pass/\nFail', 'Remarks'],
        ['OQ-001', 'Door Sensor Detection\n- Open door', 'Sensor detects door opening\nwithin 1 second', '', '', ''],
        ['OQ-002', 'Door Sensor Detection\n- Close door', 'Sensor detects door closing\nwithin 1 second', '', '', ''],
        ['OQ-003', 'Alarm Trigger\n- Manual activation', 'Alarm sounds immediately\nLED indicator ON', '', '', ''],
        ['OQ-004', 'Timer Functionality\n- Set 30 second delay', 'Timer counts down\nAlarm after 30 sec', '', '', ''],
        ['OQ-005', 'Event Logging\n- Open/close events', 'Events logged in database\nwith timestamp', '', '', ''],
        ['OQ-006', 'User Authentication\n- Login test', 'Admin login successful\nUser role verified', '', '', ''],
        ['OQ-007', 'Dashboard Display\n- Real-time status', 'Door status updates\nlive on dashboard', '', '', ''],
        ['OQ-008', 'Camera Capture\n- Event image', 'Image captured on event\n(if camera installed)', '', '', ''],
        ['OQ-009', 'Network Connectivity\n- Remote access', 'System accessible via\nLAN/Wi-Fi', '', '', ''],
        ['OQ-010', 'Audit Trail\n- Event verification', 'All events have\nblockchain hash', '', '', ''],
    ]
    
    func_table = Table(func_data, colWidths=[0.7*inch, 1.7*inch, 1.7*inch, 1.3*inch, 0.5*inch, 1.6*inch])
    func_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976d2')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(func_table)
    elements.append(PageBreak())
    
    # Performance Tests
    elements.append(Paragraph("4. PERFORMANCE TESTS", heading_style))
    perf_data = [
        ['Parameter', 'Specification', 'Actual Value', 'Pass/Fail', 'Remarks'],
        ['Sensor Response Time', '< 2 seconds', '', '', ''],
        ['Alarm Response Time', '< 1 second', '', '', ''],
        ['Event Log Write Speed', '< 500 ms', '', '', ''],
        ['Dashboard Load Time', '< 3 seconds', '', '', ''],
        ['Camera Image Quality', '≥ 720p resolution', '', '', ''],
        ['Network Latency', '< 100 ms', '', '', ''],
    ]
    
    perf_table = Table(perf_data, colWidths=[2*inch, 1.8*inch, 1.5*inch, 1*inch, 1.2*inch])
    perf_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976d2')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(perf_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Conclusion
    elements.append(Paragraph("5. CONCLUSION", heading_style))
    conclusion_text = """
    All functional and performance tests have been completed. The Door Monitoring System operates 
    as designed and meets all specified requirements. The system is deemed ready for Performance 
    Qualification (PQ).
    """
    elements.append(Paragraph(conclusion_text, styles['BodyText']))
    elements.append(Spacer(1, 0.3*inch))
    
    # Sign-off
    elements.append(Paragraph("6. SIGN-OFF", heading_style))
    signoff_data = [
        ['Role', 'Name', 'Signature', 'Date'],
        ['Tested by', '', '', ''],
        ['Verified by', '', '', ''],
        ['Approved by (QA)', '', '', ''],
    ]
    
    signoff_table = Table(signoff_data, colWidths=[2*inch, 1.8*inch, 1.8*inch, 1.9*inch])
    signoff_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976d2')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    elements.append(signoff_table)
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_pq_template_pdf(equipment_info, company_info):
    """Generate Performance Qualification (PQ) PDF Template"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                           rightMargin=0.75*inch, leftMargin=0.75*inch,
                           topMargin=1*inch, bottomMargin=0.75*inch)
    
    elements = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#d84315'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#e64a19'),
        spaceAfter=10,
        spaceBefore=15,
        fontName='Helvetica-Bold'
    )
    
    # Title
    elements.append(Paragraph("PERFORMANCE QUALIFICATION (PQ)", title_style))
    elements.append(Paragraph("Door Monitoring System - eDOMOS", styles['Heading3']))
    elements.append(Spacer(1, 0.3*inch))
    
    # Document Header
    doc_data = [
        ['Document Title:', 'Performance Qualification (PQ)'],
        ['Document No.:', f'PQ-{datetime.now().strftime("%Y-%m-%d-%H%M")}'],
        ['System Name:', equipment_info.get('name', 'eDOMOS Door Monitoring System')],
        ['Equipment Model:', equipment_info.get('model', 'eDOMOS-2.1-Pro')],
        ['Serial Number:', equipment_info.get('serial', '________________')],
        ['Date Prepared:', datetime.now().strftime('%Y-%m-%d')],
    ]
    
    doc_table = Table(doc_data, colWidths=[2.5*inch, 4*inch])
    doc_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#fbe9e7')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(doc_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Purpose
    elements.append(Paragraph("1. PURPOSE", heading_style))
    purpose_text = """
    To verify and document that the Door Monitoring System consistently performs according to 
    specifications under actual operating conditions over an extended period (typically 24-72 hours).
    """
    elements.append(Paragraph(purpose_text, styles['BodyText']))
    elements.append(Spacer(1, 0.2*inch))
    
    # Scope
    elements.append(Paragraph("2. SCOPE", heading_style))
    scope_text = """
    This PQ covers continuous performance testing of the eDOMOS system including reliability, 
    consistency, and accuracy of door monitoring, event logging, and alarm functions under 
    real-world operating conditions.
    """
    elements.append(Paragraph(scope_text, styles['BodyText']))
    elements.append(Spacer(1, 0.2*inch))
    
    # Test Duration
    elements.append(Paragraph("3. TEST DURATION", heading_style))
    duration_data = [
        ['Test Start Date/Time:', '________________'],
        ['Test End Date/Time:', '________________'],
        ['Total Duration:', '24 hours minimum (recommended: 72 hours)'],
        ['Number of Door Events:', 'Minimum 50 events'],
    ]
    
    duration_table = Table(duration_data, colWidths=[2.5*inch, 4*inch])
    duration_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(duration_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Performance Metrics
    elements.append(Paragraph("4. PERFORMANCE METRICS", heading_style))
    perf_data = [
        ['Metric', 'Acceptance Criteria', 'Measured Value', 'Pass/Fail', 'Remarks'],
        ['System Uptime', '≥ 99.9%', '', '', ''],
        ['Sensor Accuracy', '100% detection rate', '', '', ''],
        ['False Alarm Rate', '< 0.1% of events', '', '', ''],
        ['Event Log Integrity', '100% events recorded', '', '', ''],
        ['Blockchain Validation', '100% hash verified', '', '', ''],
        ['Average Response Time', '< 2 seconds', '', '', ''],
        ['Network Availability', '≥ 99%', '', '', ''],
        ['Database Growth', 'Linear, no corruption', '', '', ''],
    ]
    
    perf_table = Table(perf_data, colWidths=[2*inch, 1.5*inch, 1.3*inch, 0.8*inch, 1.9*inch])
    perf_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e64a19')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(perf_table)
    elements.append(PageBreak())
    
    # Stress Test Results
    elements.append(Paragraph("5. STRESS TEST RESULTS", heading_style))
    stress_data = [
        ['Test Scenario', 'Duration', 'Result', 'Comments'],
        ['Rapid door open/close\n(100 cycles)', '30 minutes', '', ''],
        ['Continuous operation\n(no intervention)', '24 hours', '', ''],
        ['Multiple user logins\n(concurrent)', '1 hour', '', ''],
        ['Power cycle recovery', '5 cycles', '', ''],
        ['Network disconnect/reconnect', '10 cycles', '', ''],
    ]
    
    stress_table = Table(stress_data, colWidths=[2.5*inch, 1.3*inch, 1.2*inch, 2.5*inch])
    stress_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e64a19')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(stress_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Conclusion
    elements.append(Paragraph("6. CONCLUSION", heading_style))
    conclusion_text = """
    The Door Monitoring System has successfully completed Performance Qualification testing. 
    All performance metrics meet acceptance criteria. The system consistently performs as specified 
    under real-world operating conditions. The system is validated and approved for production use.
    """
    elements.append(Paragraph(conclusion_text, styles['BodyText']))
    elements.append(Spacer(1, 0.3*inch))
    
    # Sign-off
    elements.append(Paragraph("7. SIGN-OFF", heading_style))
    signoff_data = [
        ['Role', 'Name', 'Signature', 'Date'],
        ['Tested by', '', '', ''],
        ['Verified by', '', '', ''],
        ['Approved by (QA)', '', '', ''],
    ]
    
    signoff_table = Table(signoff_data, colWidths=[2*inch, 1.8*inch, 1.8*inch, 1.9*inch])
    signoff_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e64a19')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    elements.append(signoff_table)
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer
