import os
import shutil
import subprocess


def read_source_directories(file_path):
	"""
	Read source directories from a text file, one per line.
	If the file does not exist, default to the current directory.
	:param file_path: Path to the text file containing directory paths.
	:return: A list of cleaned directory paths.
	"""
	if not os.path.exists(file_path):
		print(f"Warning: '{file_path}' not found. Defaulting to the current directory.")
		return [os.getcwd()]

	with open(file_path, 'r') as file:
		return [line.strip() for line in file if line.strip()]


def find_files_by_extension(directories, extension):
	"""
	Recursively find all files with the specified extension in the given directories.
	:param directories: List of directory paths to search in.
	:param extension: File extension to search for (e.g., ".cpp", ".ixx").
	:return: List of file paths.
	"""
	found_files = []
	for directory in directories:
		if os.path.isdir(directory):
			for root, _, files in os.walk(directory):
				for file in files:
					if file.endswith(extension):
						found_files.append(os.path.join(root, file))
		else:
			print(f"Warning: Directory '{directory}' does not exist.")
	return found_files


def build_emcc_command(cpp_files, source_directories, output_file="index.js"):
	"""
	Build the emcc command with the found .cpp files, module object files, and necessary options.
	:param cpp_files: List of .cpp file paths.
	:param source_directories: List of source directories to include as -I flags.
	:param output_file: Name of the output JS or WASM file.
	:return: The constructed emcc command as a list.
	"""
	emcc_path = shutil.which("emcc") or r"C:/emsdk/upstream/emscripten/emcc.bat"

	if not emcc_path:
		raise FileNotFoundError("Error: emcc is not accessible in the PATH.")

	print(f"Using emcc path: {emcc_path}")
	emcc_command = [emcc_path]
	emcc_command.extend(cpp_files)

	# Add -I arguments for each directory in source_directories
	for directory in source_directories:
		print(f"Adding include directory: {directory}")
		emcc_command.append("-I")
		emcc_command.append(directory)

	# Additional emcc flags
	emcc_command.extend([
		"-std=c++23",
		"-o",
		output_file,  # Output JavaScript or WASM
		"-s", "USE_GLFW=3",
		"-s", "FULL_ES2=1",
		"-s", "USE_WEBGL2=1",
		"-s", "WASM=1",
		"-s", "EXPORTED_RUNTIME_METHODS=['GL']",
		"--emrun",
		"-gsource-map"
	])
	return emcc_command


def main():
	try:
		source_file = "Source Directories.txt"

		# Read the source directories from the text file
		directories = read_source_directories(source_file)
		for directory in directories:
			if os.path.isdir(directory):
				print("Found Directory:", directory)
			else:
				print(f"Warning: Directory '{directory}' does not exist.")

		cpp_files = find_files_by_extension(directories, ".cpp")
		for file in cpp_files:
			print("Found C++ File:   ", file)

		if not cpp_files:
			print("No C++ files found. Exiting.")
			return

		# Build the emcc command with the source directories as -I arguments
		emcc_command = build_emcc_command(cpp_files, directories)
		print("Final emcc command:")
		print(" ".join(emcc_command))

		# Execute the command
		subprocess.run(emcc_command, check=True)

	except FileNotFoundError as e:
		print(e)
	except subprocess.CalledProcessError as e:
		print(f"Error during emcc execution: {e}")


if __name__ == "__main__":
	main()
