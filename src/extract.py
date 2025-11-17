import json

def extract_valid_objects(input_path, output_path):
    print("Extracting valid JSON objects from:", input_path)

    valid_objects = []
    brace_level = 0
    current_obj = []

    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:

            # Start of a new object
            if "{" in line and brace_level == 0:
                current_obj = []
                brace_level = 0

            # Track nesting
            if "{" in line:
                brace_level += line.count("{")
            if "}" in line:
                brace_level -= line.count("}")

            current_obj.append(line)

            # End of object
            if brace_level == 0 and current_obj:
                try:
                    obj_text = "".join(current_obj).strip().rstrip(",")
                    obj = json.loads(obj_text)
                    valid_objects.append(obj)
                except:
                    # Skip invalid
                    pass

                current_obj = []

    print("Extracted valid objects:", len(valid_objects))

    # Write NDJSON (one JSON per line)
    with open(output_path, "w", encoding="utf-8") as out:
        for obj in valid_objects:
            out.write(json.dumps(obj) + "\n")

    print("NDJSON written to:", output_path)
    print("Done!")
    print("This extract script is running and producing clean_data_new.ndjson")


if __name__ == "__main__":
    extract_valid_objects(
        "./data/fake_property_data_new.json",
        "./data/clean_data_new.ndjson"
    )