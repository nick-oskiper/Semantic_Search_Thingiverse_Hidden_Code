
# Note: Most of the code is hidden and only some functions are shown due to Northeastern's research policy.


# def process_and_describe(client, repo_owner, repo_name, local_extract_path, subdir, csv_writer, existing_ids, save_images=True):
#     """
#     Processes and describes each model in the repository.
#
#     Parameters:
#     - client (OpenAIClient): Instance of OpenAIClient.
#     - repo_owner (str): Owner of the repository.
#     - repo_name (str): Name of the repository.
#     - local_extract_path (str): Path where files are extracted.
#     - subdir (dict): Information about the subdirectory.
#     - csv_writer (csv.writer): CSV writer object.
#     - existing_ids (set): Set of already processed object IDs.
#     - save_images (bool): Whether to save processed images.
#     """
#     subdir_path = os.path.join(local_extract_path, subdir['path'])
#     os.makedirs(subdir_path, exist_ok=True)
#
#     try:
#         files = list_files_in_repo(repo_owner, repo_name, subdir['path'])
#     except Exception as e:
#         print(f"Error listing files in subdir {subdir['path']}: {e}")
#         return
#
#     if not files:
#         print("No files found in the repository.")
#         return
#
#     print(f"Found {len(files)} items in {subdir['path']} directory.")
#     for file_info in files:
#         if file_info['type'] == 'file' and file_info['name'].endswith('.zip'):
#             zip_path = os.path.join(subdir_path, file_info['name'])  # Path of zip file
#             try:
#                 download_file(file_info['download_url'], zip_path)  # Downloads file at path
#             except Exception as e:
#                 print(f"Skipping file due to download error: {zip_path} - {e}")
#                 continue
#
#             extract_zip(zip_path, subdir_path)  # Extracts zip to subdir
#             images_dir = os.path.join(subdir_path, 'images')
#             image_files = find_image_files(images_dir)  # Finds all images for each item
#
#             # Define the exclusion list
#             BROAD_TAGS_EXCLUSION = [
#                 "3d model", "fully assembled", "complete", "model", "assembly",
#                 "thing", "object", "product", "item", "prototype"
#             ]
#
#             if not image_files:
#                 print(f"No image files found in {zip_path}. Attempting to render using Blender.")
#                 # Locate the .stl or .obj file under 'files/' subdirectory
#                 files_subdir = os.path.join(subdir_path, 'files')
#                 if not os.path.isdir(files_subdir):
#                     print(f"No 'files/' directory found in {zip_path}. Skipping.")
#                     continue
#
#                 # Find all .stl and .obj files in 'files/' directory
#                 model_files = [f for f in os.listdir(files_subdir) if f.lower().endswith(('.stl', '.obj'))]
#                 if not model_files:
#                     print(f"No .stl or .obj files found in 'files/' directory of {zip_path}. Skipping.")
#                     continue
#
#                 # For simplicity, process the first .stl/.obj file found
#                 model_file = os.path.join(files_subdir, model_files[0])
#                 print(f"Found model file: {model_file}")
#
#                 # Define paths for Blender executable and script
#                 blender_executable = r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe"  # Update if different
#                 blender_script = ""
#                 rendered_image_path = os.path.join(subdir_path, 'rendered_image.png')
#
#                 # Call Blender to render the image
#                 rendered_image = render_model_with_blender(
#                     blender_executable,
#                     blender_script,
#                     model_file,
#                     rendered_image_path
#                 )
#
#                 if rendered_image and os.path.exists(rendered_image):
#                     image_to_use = rendered_image
#                 else:
#                     print(f"Failed to render image for {zip_path}. Skipping.")
#                     continue
#             else:
#                 # Use the largest image file if no combined image is found
#                 image_to_use = find_largest_image_file(image_files)
#                 if not image_to_use:
#                     print(f"No suitable image found in {zip_path}")
#                     continue
#
#             # Log the image being processed
#             print(f"Processing image: {image_to_use}")
#
#             # Extract keywords from the zip file name and add new keywords
#             zip_file_name = os.path.splitext(file_info['name'])[0]
#             keywords = zip_file_name.replace('-', ' ').replace('_', ' ').split()
#             keywords.extend(["complete", "assembled", "whole", "IMG_"])  # Keywords include name and these
#
#             # Generate initial guess based on the directory name
#             initial_guess = " ".join(keywords).capitalize()
#
#             # Extract object_id from subdir_path
#             id = os.path.basename(subdir_path)
#
#             # Check if object_id already exists
#             if id in existing_ids:
#                 print(f"Object ID {id} already exists in CSV. Skipping.")
#                 continue
#
#             # Generate description, category, and tags using OpenAI
#             ai_data = client.describe_image_model(image_to_use, initial_guess)
#             if ai_data:
#                 description = ai_data.get('description', '').strip()
#                 category = ai_data.get('category', '').strip()
#                 tags = ai_data.get('tags', [])
#
#                 if not description or not category or not tags:
#                     print(f"Incomplete AI data for {image_to_use}. Skipping.")
#                     continue
#
#                 # Filter out broad/generic tags
#                 filtered_tags = filter_tags(tags, BROAD_TAGS_EXCLUSION)
#
#                 # If no tags remain after filtering, assign a default tag
#                 if not filtered_tags:
#                     print(f"All tags for {image_to_use} were broad. Assigning default tag 'unknown'.")
#                     filtered_tags = ["unknown"]
#
#                 # Format tags as comma-separated string
#                 tags_str = ", ".join(filtered_tags)
#
#                 print(f"Description for {image_to_use}:\n{description}\n")
#                 print(f"Category: {category}")
#                 print(f"Tags: {tags_str}\n")
#
#                 # Derive name from the zip file name or any other logic
#                 name = " ".join(keywords).capitalize()
#
#                 # Write object_id, description, name, category, tags to CSV
#                 csv_writer.writerow([id, description, name, category, tags_str])
#                 print(f"Wrote data for Object ID {id} to CSV.\n")
#
#                 # Add to existing_ids to prevent reprocessing within the same run
#                 existing_ids.add(id)
#
#             # Save a copy of the image being processed for visual inspection if save_images is True
#             if save_images:
#                 try:
#                     output_dir = os.path.join(local_extract_path, 'processed_images')  # Puts them to processed_images
#                     os.makedirs(output_dir, exist_ok=True)
#                     img_output_path = os.path.join(output_dir, os.path.basename(image_to_use))  # Good for verifying correctness of GPT
#
#                     # Ensure path length is within acceptable limits
#                     if len(img_output_path) > 255:
#                         print(f"Path too long: {img_output_path}")
#                         continue
#
#                     # Save the image file
#                     with open(image_to_use, 'rb') as img_file:
#                         with open(img_output_path, 'wb') as output_file:
#                             output_file.write(img_file.read())
#                     print(f"Saved processed image to: {img_output_path}")
#                 except Exception as e:
#                     print(f"Error saving image {image_to_use}: {e}")
#
#             # Pause to manage load
#             time.sleep(1)
#
#
# def main(repo_owner, repo_name, local_extract_path='.', save_images=True):
#     """
#     Main function to orchestrate the scraping and description generation.
#
#     Parameters:
#     - repo_owner (str): Owner of the GitHub repository.
#     - repo_name (str): Name of the GitHub repository.
#     - local_extract_path (str): Local path where files will be extracted.
#     - save_images (bool): Whether to save processed images.
#     """
#     client = OpenAIClient()
#
#     # CSV output file
#     output_csv = os.path.join(local_extract_path, 'thing_descriptions_main.csv')
#
#     # Load existing object IDs to enable resume capability
#     existing_ids = load_existing_object_ids(output_csv)
#
#     # Open the CSV file for appending descriptions
#     with open(output_csv, mode='a', newline='', encoding='utf-8') as file:
#         csv_writer = csv.writer(file)
#
#         # Write header if file doesn't exist or is empty
#         if not os.path.exists(output_csv) or os.path.getsize(output_csv) == 0:
#             csv_writer.writerow(['id', 'description', 'name', 'category', 'tags'])
#             print(f"Created CSV file with headers at {output_csv}.")
#
#         # Download and describe image files one by one
#         try:
#             subdirs = list_files_in_repo(repo_owner, repo_name, "downloaded_files")
#             for subdir in subdirs:
#                 if subdir['type'] == 'dir':
#                     id = os.path.basename(subdir['path'])
#                     if id in existing_ids:
#                         print(f"Object ID {id} already exists in CSV. Skipping subdir.")
#                         continue  # Skip processing this subdir
#                     else:
#                         process_and_describe(client,repo_owner,repo_name,local_extract_path,subdir,csv_writer,existing_ids,save_images)
#             print("Finished processing image files.")
#         except Exception as e:
#             print(f"Error processing files: {e}")
#             return

