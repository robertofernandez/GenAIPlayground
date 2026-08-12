print("El script ha empezado a ejecutarse")

import os

# Define the project structure
PROJECT_STRUCTURE = {
    "skill_extraction": {
        "app": {
            "api": {
                "v1": {
                    "routes.py": "",
                },
            },
            "core": {
                "config.py": "",
                "utils.py": "",
            },
            "models": {
                "job_description.py": "",
                "skill_response.py": "",
                "base_model.py": "",
            },
            "prompts": {
                "skill_extraction_prompt.txt": "",
            },
            "providers": {
                "anthropic_provider.py": "",
            },
            "services": {
                "skill_extraction_service.py": "",
            },
            "main.py": "",
        },
        "tests": {
            "test_routes.py": "",
            "test_services.py": "",
            "test_providers.py": "",
        },
        ".env": "",
        "requirements.txt": "",
        "README.md": "",
    }
}

def create_project_structure(base_path, structure):
    """
    Recursively create the folder structure and files.
    If a file or directory already exists, it will be left unchanged.
    """
    for name, content in structure.items():
        path = os.path.join(base_path, name)
        if isinstance(content, dict):
            # Create a directory
            os.makedirs(path, exist_ok=True)
            create_project_structure(path, content)
        else:
            # Create a file
            if not os.path.exists(path):
                with open(path, "w") as f:
                    f.write(content)

if __name__ == "__main__":
    base_path = os.getcwd()
    print(f"Creando estructura en: {base_path}")  # Debug
    create_project_structure(base_path, PROJECT_STRUCTURE)
    print("Project structure created successfully!")