
# Note: Most of the code is hidden and only some functions are shown due to Northeastern's research policy.


# def process_and_describe(client, repo_owner, repo_name, local_extract_path, subdir, github_csv_url, csv_writer, existing_ids, save_images=True):
#     subdir_path = os.path.join(local_extract_path, subdir)
#     os.makedirs(subdir_path, exist_ok=True)
#
#     try:
#         files = list_files_in_repo(repo_owner, repo_name, subdir)
#     except Exception as e:
#         print(f"Error listing files in subdir {subdir}: {e}")
#         return
#
#     if not files:
#         print("No files found in the repository.")
#         return
#
#     print(f"Found {len(files)} items in {subdir} directory.")
#     for file_info in files:
#         if file_info['type'] == 'file' and file_info['name'].endswith('.zip'):
#             zip_path = os.path.join(subdir_path, file_info['name'])
#             try:
#                 download_file(file_info['download_url'], zip_path)
#             except Exception as e:
#                 print(f"Skipping file due to download error: {zip_path} - {e}")
#                 continue
#
#             extract_zip(zip_path, subdir_path)
#             images_dir = os.path.join(subdir_path, 'images')
#             image_files = find_image_files(images_dir)
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
#                 blender_script = ""  # Path to the simplified Blender script
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
#             object_id = os.path.basename(subdir)
#
#             # Check if object_id already exists
#             if object_id in existing_ids:
#                 print(f"Object ID {object_id} already exists in CSV. Skipping.")
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
#                 # Write id, name, description, category, tags to CSV
#                 csv_writer.writerow([object_id, name, description, category, tags_str])
#                 print(f"Wrote data for Object ID {object_id} to CSV.\n")
#
#                 # Add to existing_ids to prevent reprocessing within the same run
#                 existing_ids.add(object_id)
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
#             # Adding a pause to manage load
#             time.sleep(1)
#
# def render_model_with_blender(blender_executable, blender_script, model_path, output_image_path):
#     """
#     Calls Blender via subprocess to render the model and save the screenshot.
#
#     Parameters:
#     - blender_executable (str): Path to the Blender executable.
#     - blender_script (str): Path to the Blender rendering script.
#     - model_path (str): Path to the .stl or .obj file.
#     - output_image_path (str): Path where the rendered image will be saved.
#
#     Returns:
#     - str or None: Path to the rendered image if successful, else None.
#     """
#     try:
#         subprocess.run([
#             blender_executable,
#             '-b',
#             '-P', blender_script,
#             '--',
#             model_path,
#             output_image_path
#         ], check=True)
#         print(f"Rendered image saved at: {output_image_path}")
#         return output_image_path
#     except subprocess.CalledProcessError as e:
#         print(f"Blender rendering failed: {e}")
#         return None
#
# def main(repo_owner, repo_name, github_csv_url, local_extract_path='.', save_images=True):
#     client = OpenAIClient()
#
#     output_csv = os.path.join(local_extract_path, 'thing_descriptions.csv')
#     existing_ids = set()
#
#     # Define CSV headers
#     csv_headers = ['id', 'name', 'AI generated summary', 'category', 'tags']
#
#     # Load existing object IDs to enable resume capability
#     if os.path.exists(output_csv):
#         try:
#             with open(output_csv, mode='r', newline='', encoding='utf-8') as file:
#                 csv_reader = csv.reader(file)
#                 headers = next(csv_reader, None)  # Read header
#                 for row in csv_reader:
#                     if row:
#                         existing_ids.add(row[0])  # Assuming 'id' is the first column
#             print(f"Loaded {len(existing_ids)} existing object IDs from CSV.")
#         except Exception as e:
#             print(f"Error reading existing CSV file: {e}")
#
#     # Open the CSV file for appending descriptions
#     with open(output_csv, mode='a', newline='', encoding='utf-8') as file:
#         csv_writer = csv.writer(file)
#
#         # Write header if file doesn't exist or is empty
#         if not os.path.exists(output_csv) or os.path.getsize(output_csv) == 0:
#             csv_writer.writerow(csv_headers)
#             print(f"Created CSV file with headers at {output_csv}.")
#
#         print("Listing and processing image files...")
#         try:
#             subdirs = list_files_in_repo(repo_owner, repo_name, "downloaded_files")
#             for subdir in subdirs:
#                 if subdir['type'] == 'dir':
#                     # Extract the thingid from the directory name
#                     thingid = os.path.basename(subdir['path'])
#
#                     # Check if the thingid already exists
#                     if thingid in existing_ids:
#                         print(f"ThingID {thingid} already exists in the CSV. Skipping.")
#                         continue  # Skip this thingid
#
#                     # Process the description and write to CSV if not found
#                     process_and_describe(
#                         client,
#                         repo_owner,
#                         repo_name,
#                         local_extract_path,
#                         subdir['path'],
#                         github_csv_url,
#                         csv_writer,
#                         existing_ids,
#                         save_images
#                     )
#             print("Finished processing image files.")
#         except Exception as e:
#             print(f"Error processing files: {e}")
#
