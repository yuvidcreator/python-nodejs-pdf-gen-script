import subprocess
import os
import time
import base64
from io import BytesIO
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import json
import tempfile
from functools import lru_cache
# from concurrent.futures import ThreadPoolExecutor
import logging

# Configure matplotlib for better performance
matplotlib.use('Agg')  # Use non-interactive backend
plt.ioff()  # Turn off interactive mode

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFGenerator:
    """Optimized PDF Generator with caching and memory management"""
    
    def __init__(self, output_dir='output', images_dir='public/images'):
        self.output_dir = output_dir
        self.images_dir = images_dir
        self._ensure_directories()
        
    def _ensure_directories(self):
        """Create necessary directories if they don't exist"""
        for directory in [self.output_dir, self.images_dir]:
            os.makedirs(directory, exist_ok=True)
    
    @lru_cache(maxsize=128)
    def _calculate_radar_positions(self, n_points=6):
        """Cache radar chart angle calculations"""
        return [np.pi/2 - 2*np.pi*i/n_points for i in range(n_points)]
    
    def _create_radar_grid(self, ax, angles, max_value=100):
        """Optimized radar grid creation"""
        # Pre-calculate grid values
        grid_values = range(25, max_value + 1, 25)
        
        for radial_value in grid_values:
            # Calculate grid coordinates once
            grid_coords = [(radial_value * np.cos(theta), radial_value * np.sin(theta)) 
                            for theta in angles]
            grid_coords.append(grid_coords[0])  # Close the polygon
            
            grid_x, grid_y = zip(*grid_coords)
            
            line_props = {
                'color': '#333333' if radial_value == max_value else 'gray',
                'linewidth': 1.5 if radial_value == max_value else 0.5,
                'linestyle': '-' if radial_value == max_value else '--',
                'alpha': 1.0 if radial_value == max_value else 0.7
            }
            ax.plot(grid_x, grid_y, **line_props)
    
    def _add_radar_labels(self, ax, angles, max_value=100):
        """Add percentage labels to radar chart"""
        label_angle = -np.pi/6  # -30 degrees
        
        for radial_value in range(25, max_value + 1, 25):
            x_label = (radial_value * 0.90) * np.cos(label_angle)
            y_label = (radial_value * 0.90) * np.sin(label_angle)
            
            ax.text(x_label, y_label, f'{radial_value}%', 
                    ha='right', va='top', color='gray', fontsize=9,
                    fontfamily='Arial',
                    bbox=dict(facecolor='#F1F9FF', alpha=0.8, 
                    edgecolor='none', pad=1))
    
    def generate_radar_chart(self, data, save_formats=['svg']):
        """
        Generate optimized radar chart with multiple format support
        
        Args:
            data: Input data dictionary
            save_formats: List of formats to save ['svg', 'webp', 'png']
        
        Returns:
            dict: Base64 encoded data for each requested format
        """
        try:
            # Extract data efficiently
            genetic_results = data["EDAPPGS006"]["ResultInfo"]["genetic_results"]
            categories = [value["holland_code"] for value in genetic_results.values()]
            values = [int(value["result"]) for value in genetic_results.values()]
            
            n = len(categories)
            angles = self._calculate_radar_positions(n)
            
            # Calculate coordinates
            coords = [(v * np.cos(theta), v * np.sin(theta)) 
                    for v, theta in zip(values, angles)]
            coords.append(coords[0])  # Close polygon
            x_coords, y_coords = zip(*coords)
            
            # Create figure with optimized settings
            fig, ax = plt.subplots(figsize=(8, 8), dpi=150)
            
            # Add grid and labels
            self._create_radar_grid(ax, angles)
            self._add_radar_labels(ax, angles)
            
            # Add spokes
            for theta in angles:
                ax.plot([0, 100*np.cos(theta)], [0, 100*np.sin(theta)], 
                        '--', color='gray', linewidth=0.5, alpha=0.5)
            
            # Plot data
            ax.plot(x_coords, y_coords, linewidth=2, color='#6A1B9A', zorder=3)
            ax.fill(x_coords, y_coords, alpha=0.2, color='#E6E6FA', zorder=3)
            
            # Add center point
            ax.plot(0, 0, 'ko', markersize=8, zorder=4)
            ax.text(0, -3, '0%', ha='center', va='top', 
                    color='black', fontsize=9, zorder=5)
            
            # Final formatting
            ax.set_aspect('equal')
            ax.axis('off')
            plt.xlim(-120, 120)
            plt.ylim(-120, 120)
            
            # Save in requested formats
            results = {}
            
            for fmt in save_formats:
                buffer = BytesIO()
                
                if fmt == 'svg':
                    plt.savefig(buffer, format='svg', dpi=150, 
                                bbox_inches='tight', pad_inches=0.1, transparent=True)
                elif fmt == 'webp':
                    filename = os.path.join(self.images_dir, 'radar_chart.webp')
                    plt.savefig(filename, format='webp', dpi=150, 
                                pil_kwargs={"lossless": False}, 
                                bbox_inches='tight', pad_inches=0.1, transparent=True)
                    # Also save to buffer for base64
                    plt.savefig(buffer, format='png', dpi=150, 
                                bbox_inches='tight', pad_inches=0.1, transparent=True)
                else:  # png or other formats
                    plt.savefig(buffer, format=fmt, dpi=150, 
                                bbox_inches='tight', pad_inches=0.1, transparent=True)
                
                buffer.seek(0)
                results[fmt] = base64.b64encode(buffer.read()).decode('utf-8')
                buffer.close()
            
            # Clean up
            plt.close(fig)
            
            logger.info("Radar chart generated successfully")
            return results
            
        except Exception as e:
            logger.error(f"Error generating radar chart: {e}")
            raise
    
    def prepare_pdf_data(self, raw_data):
        """Prepare and enrich data for PDF generation"""
        try:
            # Generate radar chart
            chart_data = self.generate_radar_chart(raw_data, ['svg'])
            raw_data["RadarGraphBase64"] = chart_data['svg']
            
            return raw_data
            
        except Exception as e:
            logger.error(f"Error preparing PDF data: {e}")
            raise
    
    def generate_pdf_subprocess(self, data, output_path='output/final.pdf'):
        """
        Generate PDF using Node.js subprocess with optimized data passing
        
        Args:
            data: Dictionary containing PDF data
            output_path: Output file path
        """
        # try:
        # Prepare data
        prepared_data = self.prepare_pdf_data(data)
        
        # Convert to compact JSON
        json_string = json.dumps(prepared_data)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # node_script_path = os.path.join(os.path.dirname(__file__), 'cli.js')
        
        # Run Node.js process with optimized settings
        process = subprocess.run([
            'node', 'cli.js',
            '--data', json_string,
            '--output', output_path
        ], check=True)
        
        # return output_path
            
        if process.returncode == 0:
            logger.info(f"✅ PDF generated successfully: {output_path}")
            return output_path
        else:
            logger.error(f"Node.js process failed: {process.stderr}")
            logger.error(f"Reason --> {process.args, process.stdout}")
            raise subprocess.CalledProcessError(process.returncode, 'node')


SAMPLE_DATA = {
    "OrderInfo": {
        "id": "597",
        "order_id": "OAT250300005",
        "assign_type": "product",
        "product_code": "EDAPPGS006",
        "product_category": "GSA",
        "product_sub_category": "GSA",
        "product_name_en": "AptitudePlus",
        "product_name_kr": "AptitudePlus",
        "package_code": "",
        "package_name_en": "",
        "package_name_kr": "",
        "report_provider": "reportlab",
        "patient_name": "aptitude_ED01_EN",
        "patient_dob": "1993-05-10",
        "patient_gender": "M",
        "patient_address": "",
        "patient_height": "",
        "patient_weight": "",
        "patient_email": "",
        "patient_contact": "",
        "patient_nationality": "",
        "guardian_name": "",
        "guardian_relation": "",
        "guardian_contact": "",
        "order_category": "domestic",
        "sample_collection_date": "2025-03-03",
        "sample_collection_time": "",
        "sample_receipt_date": "2025-03-04",
        "sample_receipt_by": "system",
        "sample_specimen_type": "BLOOD",
        "sample_barcode": [
            {
                "sample_barcode": "jhgbvfdc",
                "no_of_tubes": "1"
            }
        ],
        "barcode_receive_status": "True",
        "sample_barcode_receive": "{\"jhgbvfdc\": 1}",
        "sample_resampling": "",
        "previous_order_id": "",
        "sample_resampling_date": "",
        "sample_resampling_time": "",
        "sample_report_id": "",
        "provider_order_id": "",
        "available_for_research_purpose": "",
        "name_anonymised": "",
        "confirmatory_test": "",
        "vip_test": "",
        "trf_consent": "True",
        "trf_form": "",
        "trf_form_received": "",
        "gen_test_consent": "True",
        "guardian_consent_form": "",
        "guardian_consent_form_received": "",
        "human_material_rnd_consent": "",
        "diagnomics_irb_rnd_consent": "",
        "process_notification_consent": "",
        "marketing_info_rec_consent": "",
        "sharing_3party_consent": "",
        "sample_tag": "",
        "sample_suitability": "True",
        "dna_quality": "True",
        "data_quality": "True",
        "ref_material_test": "True",
        "data_file": "[\"OAT250300005_data_file_2025_03_04_17_44_08_60184_208740500032_R08C02_25-00458_gsa_report.txt.gz\"]",
        "order_type": "raw_data",
        "lab_qc_flag": "",
        "lab_qc_comment": "",
        "lab_status": "",
        "report_version": "ED_01",
        "report_language": "EN",
        "report_type": "original",
        "report_file": "",
        "report_date": "",
        "storage_provider_id": "C0001",
        "storage_provider_name": "EDGC_client",
        "report_email_receiver_id": "P0001",
        "report_email_receiver_name": "Payal garg",
        "order_status": "ST204",
        "order_status_message": "Data analysis completed",
        "result": "",
        "report_server_json_response": "",
        "reg_date": "2025-03-04 17:44:18",
        "update_date": "2025-03-04 17:48:54",
        "reg_by": "admin",
        "operator": "system",
        "printout_required": "",
        "show_fetus_gender": "",
        "flag": "",
        "review_flag": "",
        "review_comment": "",
        "paid_unpaid": "paid",
        "collection_kit": "",
        "chart_number": "",
        "hospital_sample_number": "",
        "chip_type": "",
        "gestational_age": "",
        "measurement_date": "",
        "measurement_method": "",
        "inspection_type": "",
        "inspection_item": "",
        "clinical_findings": "",
        "additional_information": "",
        "order_log": "[[\"2025-03-04 17:44:57\", \"system\"], [\"2025-03-04 17:45:47\", \"system\"], [\"2025-03-04 17:46:29\", \"system\"], [\"2025-03-04 17:48:50\", \"system\"], [\"2025-03-04 17:48:54\", \"system\"]]",
        "client_id": "C0001",
        "client_comp_short_name": "EDGC_client",
        "client_comp_full_name": "EDGC_client",
        "client_comp_phone": "3898989898989",
        "client_comp_address": "EDGC_clientEDGC_clientEDGC_clientEDGC_clientEDGC_client",
        "partner_id": "P0001",
        "partner_comp_short_name": "EDGC_partner",
        "partner_comp_full_name": "Payal garg",
        "partner_comp_phone": "07877766268",
        "partner_comp_address": "32/33 MAMTA NIWAS ADARSH NAGAR, KHUNADI KOTA\nKHUNADI KOTA",
        "hospital_id": "H0003",
        "hospital_short_name": "hospital3",
        "assign_product_reference": "12",
        "hospital_full_name": "hospital3",
        "hospital_phone": "13256645465446",
        "hospital_address": "hospital3hospital3hospital3hospital3hospital4",
        "doctor_id": "",
        "doctor_short_name": "",
        "doctor_full_name": "",
        "doctor_phone": "",
        "doctor_address": "",
        "upload_option_req": "",
        "batch_id": "",
        "is_control_sample": "",
        "lab_out_sourcing": "",
        "lab_provider_id": "",
        "lab_provider_short_name": "",
        "lab_provider_data_folder": "",
        "is_Family": "",
        "family_detail": "",
        "shipping_company_name": "",
        "tracking_number": "",
        "test_result": "",
        "client_report_registor_response": "",
        "clinical_confirmatory_test": "",
        "clinical_confirmatory_test_result": "",
        "clinical_confirmatory_test_result_file": "",
        "invoice_completed": "",
        "lab_provider_api_status": "",
        "lab_provider_api_response": "",
        "logo": "https://for-hsflow.s3.amazonaws.com/dev/users/partner_logo/P0001_partner_logo.jpg?response-content-type=image%2Fjpeg&AWSAccessKeyId=AKIAQEO6MCRPTS6WYCHU&Signature=zAy3BXvJpGawkFZHSS7yCWw6NUo%3D&Expires=1743670139&ResponseContentDisposition=inline"
    },
    "EDAPPGS006": {
        "Summary": {
            "report_version": "ED_01",
            "report_type": "original"
        },
        "ResultInfo": {
            "genetic_results": {
                "A_results": {
                    "item_code": "A",
                    "holland_code": "Artistic",
                    "feature_name": "Novelty Seeking",
                    "GENE": "DBH",
                    "RSID": "rs7040170",
                    "genotype": "AA",
                    "result": "30",
                    "comment": "Adventurous but has the average sentimentality."
                },
                "C_results": {
                    "item_code": "C",
                    "holland_code": "Conventional",
                    "feature_name": "Avoidance of Errors",
                    "GENE": "DRD2",
                    "RSID": "rs1800497",
                    "genotype": "AG",
                    "result": "50",
                    "comment": "Relatively good at learning from one’s own mistake."
                },
                "E_results": {
                    "item_code": "E",
                    "holland_code": "Enterprising",
                    "feature_name": "Warrier vs. Worrier",
                    "GENE": "COMT",
                    "RSID": "rs4680",
                    "genotype": "GG",
                    "result": "90",
                    "comment": "Extrovert. Strong-minded and optimistic. Resilient to pain, courageous and loyal to people. Has strong people skills."
                },
                "I_results": {
                    "item_code": "I",
                    "holland_code": "Investigative",
                    "feature_name": "Recognize Faces",
                    "GENE": "MET",
                    "RSID": "rs2237717",
                    "genotype": "CC",
                    "result": "90",
                    "comment": "Has high neurocognition ability and face recognition skill."
                },
                "R_results": {
                    "item_code": "R",
                    "holland_code": "Realistic",
                    "feature_name": "Performance IQ",
                    "GENE": "SNAP25",
                    "RSID": "rs363050",
                    "genotype": "AG",
                    "result": "50",
                    "comment": "Has average performance IQ and spatial ability."
                },
                "S_results": {
                    "item_code": "S",
                    "holland_code": "Social",
                    "feature_name": "Socio-Emotional Sensitivity",
                    "GENE": "OXTR",
                    "RSID": "rs53576",
                    "genotype": "AA",
                    "result": "30",
                    "comment": "Less empathetic. Prefers to spend time alone."
                }
            },
            "result_type": [
                "E",
                "I",
                "C"
            ],
            "result_type_full": [
                "Enterprising",
                "Investigative",
                "Conventional"
            ],
            "result_percentage": [
                90,
                90,
                50
            ],
            "interest_1_title": "A man of leadership",
            "interest_1_comment": "You are extroverted, competitive and confident. You are very well spoken, optimistic and have great leadership skills. As a goal oriented person, you are talented in performing operational and sales work. You are at once sociable and responsible.",
            "personality_1_title": "Leading, Persuading and Performing",
            "personality_1_comment": "You are someone who has strong desire for winning and seeks to be a leader. Likely to function most effectively in a competitive environment with great confidence and presentation skills, but may need further effort in developing detail-oriented mindset.",
            "interest_2_title": "A man of thought",
            "interest_2_comment": "Scholastic, analyzing and exploratory. You like to explore and investigate scientific and social phenomenon. You have an exceptional math and science ability and highly inquisitive personality.",
            "personality_2_title": "Observing, Analyzing, and Scientific",
            "personality_2_comment": "You are someone who is very logical, intelligent and academically motivated. However, you may require more effort in making independent decisions and in understanding our community as a whole.",
            "interest_3_title": "A man of convention",
            "interest_3_comment": "You are a strategic, responsible person who loves to have things in order. You find yourself organizing and recording often, and you have strong office and mathematical skills.",
            "personality_3_title": "Planning, Organizing and Analyzing",
            "personality_3_comment": "You are someone who prefers strategic planning and who are good at managing different variables in the most productive configuration possible. However, you have a low tendency to explore something new and seek for adventures. Constantly push yourself to acquire diverse experiences in life.",
            "combination_1": [
                "E",
                "I"
            ],
            "combination_1_majors": [
                "Biology",
                "Business",
                "Business Administration",
                "Chemistry",
                "Commerce and Trade",
                "Hotel Management",
                "Law",
                "Marine Science",
                "Mass Communication",
                "Math",
                "Medicine",
                "Patent Law",
                "Physics",
                "Political Science"
            ],
            "combination_1_careers": [
                "Actuary",
                "Advertising Executive",
                "Advertising Sales Rep",
                "Agronomist",
                "Anesthesiologist",
                "Anthropologist",
                "Archaeologist",
                "Banker/Financial Planner",
                "Biochemist",
                "Biologist",
                "Branch Manager",
                "Business Manager",
                "Buyer",
                "Chamber of Commerce Exec",
                "Chemical Engineer",
                "Chemist",
                "Computer Systerms Analyst",
                "Credit Analyst",
                "Customer Service Manage",
                "Dentist",
                "Ecologist",
                "Economist",
                "Education & Training Manager",
                "Electric Engineer",
                "Emergency Medical Technician",
                "Entrepreneur",
                "Foreign Service Officer",
                "Funeral Director",
                "Geologist",
                "Horticulturist",
                "Insurance Manager",
                "Interpreter",
                "Lawyer/Attorney",
                "Lobbyist",
                "Mathematician",
                "Medical Technologist",
                "Meteorologist",
                "Nurse Practitioner",
                "Office Manager",
                "Personnel Recruiter",
                "Pharmacist",
                "Politicain",
                "Psychologist",
                "Public Relations Rep",
                "Research Analyst",
                "Retail Store Manager",
                "Sales Manager",
                "Sales Representative",
                "Social Service Director",
                "Statisticain",
                "Stockbroker",
                "Surgeon",
                "Tax Accountant",
                "Technical Writer",
                "Veterinarian"
            ],
            "combination_2": [
                "I",
                "C"
            ],
            "combination_2_majors": [
                "Accounting",
                "Biology",
                "Chemistry",
                "Finance",
                "Information Processing",
                "Information Science",
                "Law",
                "Marine Science",
                "Math",
                "Medicine",
                "Patent Law",
                "Physics",
                "Public Administration",
                "Real Estate",
                "Statistics"
            ],
            "combination_2_careers": [
                "Accountant",
                "Actuary",
                "Administrative Assistant",
                "Agronomist",
                "Anesthesiologist",
                "Anthropologist",
                "Archaeologist",
                "Biochemist",
                "Biologist",
                "Budget Analyst",
                "Business Manager",
                "Business Programmer",
                "Business Teacher",
                "Catalog Librarian",
                "Chemical Engineer",
                "Chemist",
                "Claims Adjuster",
                "Computer Operator",
                "Computer Systerms Analyst",
                "Congressional-District Aide",
                "Cost Accountant",
                "Court Reporter",
                "Credit Manager",
                "Customs Inspector",
                "Dentist",
                "Ecologist",
                "Economist",
                "Editorial Assistant",
                "Electric Engineer",
                "Elementary School Teacher",
                "Financial Analyst",
                "Geologist",
                "Horticulturist",
                "Insurance Manager",
                "Insurance Underwriter",
                "Internal Auditor",
                "Kindergarten Teacher",
                "Mathematician",
                "Medical Records Technician",
                "Medical Technologist",
                "Meteorologist",
                "Museum Registrar",
                "Nurse Practitioner",
                "Paralegal",
                "Pharmacist",
                "Psychologist",
                "Research Analyst",
                "Safety Inspector",
                "Statisticain",
                "Surgeon",
                "Tax Accountant",
                "Tax Consultant",
                "Technical Writer",
                "Travel Agent",
                "Veterinarian"
            ],
            "combination_3": [
                "C",
                "E"
            ],
            "combination_3_majors": [
                "Accounting",
                "Business",
                "Business Administration",
                "Commerce and Trade",
                "Finance",
                "Hotel Management",
                "Information Processing",
                "Information Science",
                "Law",
                "Mass Communication",
                "Math",
                "Political Science",
                "Public Administration",
                "Real Estate",
                "Statistics"
            ],
            "combination_3_careers": [
                "Accountant",
                "Administrative Assistant",
                "Advertising Executive",
                "Advertising Sales Rep",
                "Banker/Financial Planner",
                "Branch Manager",
                "Budget Analyst",
                "Business Manager",
                "Business Programmer",
                "Business Teacher",
                "Buyer",
                "Catalog Librarian",
                "Chamber of Commerce Exec",
                "Claims Adjuster",
                "Computer Operator",
                "Congressional-District Aide",
                "Cost Accountant",
                "Court Reporter",
                "Credit Analyst",
                "Credit Manager",
                "Customer Service Manage",
                "Customs Inspector",
                "Editorial Assistant",
                "Education & Training Manager",
                "Elementary School Teacher",
                "Emergency Medical Technician",
                "Entrepreneur",
                "Financial Analyst",
                "Foreign Service Officer",
                "Funeral Director",
                "Insurance Manager",
                "Insurance Underwriter",
                "Internal Auditor",
                "Interpreter",
                "Kindergarten Teacher",
                "Lawyer/Attorney",
                "Lobbyist",
                "Medical Records Technician",
                "Museum Registrar",
                "Office Manager",
                "Paralegal",
                "Personnel Recruiter",
                "Politicain",
                "Public Relations Rep",
                "Retail Store Manager",
                "Safety Inspector",
                "Sales Manager",
                "Sales Representative",
                "Social Service Director",
                "Stockbroker",
                "Tax Accountant",
                "Tax Consultant",
                "Travel Agent"
            ]
        }
    }
}


def main():
    """Main execution function with error handling and timing"""
    start_time = time.time()
    
    try:
        # Initialize generator
        pdf_gen = PDFGenerator()
        
        output_path = 'output/optimized_final.pdf'
        
        # Generate PDF
        output_file = pdf_gen.generate_pdf_subprocess(
            SAMPLE_DATA, 
            output_path
        )
        
        execution_time = time.time() - start_time
        file_size = os.path.getsize(output_file) / 1024  # KB
        
        logger.info(f"✅ Optimization Complete!")
        logger.info(f"📄 File: {output_file}")
        logger.info(f"📏 Size: {file_size:.1f} KB")
        logger.info(f"⏱️  Time: {execution_time:.2f} seconds")
        
    except Exception as e:
        logger.error(f"❌ Generation failed: {e}")
        raise

if __name__ == '__main__':
    main()