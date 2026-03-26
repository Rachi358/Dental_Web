import os
import shutil
import json
import sys

def setup_new_client():
    print("🦷 Welcome to the Dental Client Setup Script!")
    print("------------------------------------------")
    
    # Target directory for the new client
    client_folder_name = input("Enter new client folder name (e.g., 'HappyTeeth'): ").strip()
    
    if not client_folder_name:
        print("Folder name cannot be empty. Exiting.")
        sys.exit(1)
        
    # Paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    new_client_dir = os.path.normpath(os.path.join(base_dir, '..', client_folder_name))
    
    if os.path.exists(new_client_dir):
        print(f"Error: Directory '{new_client_dir}' already exists.")
        sys.exit(1)
        
    # Gather basic details
    clinic_name = input("Enter Clinic Name: ").strip()
    tagline = input("Enter Tagline: ").strip()
    phone = input("Enter Primary Phone (e.g., +91...): ").strip()
    whatsapp = input("Enter WhatsApp Number (only digits e.g., 91987...): ").strip()
    admin_password = input("Enter new admin password: ").strip()

    print(f"\nCloning project to {new_client_dir}...")
    
    # Copy project structure
    # Define files and folders to copy
    items_to_copy = ['app.py', 'config.json', 'requirements.txt', 'templates', 'static']
    
    os.makedirs(new_client_dir)
    
    for item in items_to_copy:
        src = os.path.join(base_dir, item)
        dst = os.path.join(new_client_dir, item)
        
        if os.path.exists(src):
            if os.path.isdir(src):
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
    
    # Update config.json in the new client directory
    new_config_path = os.path.join(new_client_dir, 'config.json')
    if os.path.exists(new_config_path):
        with open(new_config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
            
        # Update values
        config_data["clinic_name"] = clinic_name if clinic_name else config_data["clinic_name"]
        config_data["tagline"] = tagline if tagline else config_data["tagline"]
        config_data["phone"] = phone if phone else config_data["phone"]
        config_data["whatsapp"] = whatsapp if whatsapp else config_data["whatsapp"]
        if admin_password:
            config_data["admin_password"] = admin_password
            
        # Clear out test payment keys so new client secures their own
        if "payment" in config_data:
            config_data["payment"]["razorpay_key_id"] = "YOUR_OWN_RAZORPAY_KEY"
            config_data["payment"]["razorpay_key_secret"] = "YOUR_OWN_SECRET"
            config_data["payment"]["enabled"] = False
        
        # Write back
        with open(new_config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=4)
            
    print("\n✅ Setup Complete!")
    print(f"Client project is ready at: {new_client_dir}")
    print("Next steps:")
    print(f"1. cd ../{client_folder_name}")
    print("2. pip install -r requirements.txt (if not already installed)")
    print("3. python app.py")

if __name__ == '__main__':
    setup_new_client()
