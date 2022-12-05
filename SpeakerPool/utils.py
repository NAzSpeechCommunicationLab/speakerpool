import os
from SpeakerPool.models import db, StudyEntry

def get_studyname(study_id):
    current_study = StudyEntry.query.get(study_id) # get the current study
    return current_study.study_name # get study name

def get_study_dict():
    studies = [os.path.basename(x[0]) for x in os.walk(os.path.join(r"./static/studies")) if x[0] != r"./static/studies"]
    studies_in_db = [entry for entry in StudyEntry.query.all()]
    studies_list = []
    for entry in studies_in_db:
        if entry.id not in studies:
            studies_in_db.remove(entry)
        study_dict = {}
        study_dict["id"] = entry.id
        study_dict["study_name"] = entry.study_name
        study_dict["participant_description"] = entry.participant_description
        study_dict["text_type"] = entry.text_type
        study_dict["n_participants"] = entry.n_participants
        study_dict["n_recordings"] = entry.n_recordings
        study_dict["total_recording"] = entry.total_recording
        study_dict["demographic_info"] = list(get_demographic(entry.id).keys())
        studies_list.append(study_dict)
        return studies_list
        
def get_demographic(study_id):
    filename = r"./SpeakerPool/static/studies/%s/demographic.txt" % study_id
    demographic_dict = {}
    with open(filename, "r") as f:
        lines = f.readlines()
        for line in lines:
            line = line.split("\t")
            demographic_dict[line[0]] = line[1].strip("\n")
    return demographic_dict

def done_demographic(study_id, current_user):
    filename = r"./SpeakerPool/static/studies/"+str(study_id)+"/data/demographic/"+str(current_user.id)+".txt"
    if os.path.isfile(filename):
        with open(filename, "r") as f:
            n_lines = len(f.readlines())
            if n_lines > 2:
                return True
    return False

def gen_prompt_dict(study_id):
    filename = r"./SpeakerPool/static/studies/"+str(study_id)+"/prompts.txt"
    dict_filepath = "./SpeakerPool/static/studies/" + str(study_id) + "/data/enumeration.txt"
    generate_enum = False
    if not os.path.isfile(dict_filepath):
        generate_enum = True
    with open(filename, "r", encoding="cp1252") as f:
        # prompts = f.readlines()
        prompt_dict = {}
        idx = 1
        for line in f:
            prompt = line.strip("\n")
            if prompt != "RANDOMIZE":
                prompt_dict[prompt] = idx
                if generate_enum:
                    with open(dict_filepath, "a") as dict_file:
                        line = str(idx) + "\t" + str(prompt) + "\n"
                        dict_file.write(line)
                idx += 1
    return prompt_dict

def check_for_participation(study_id, participant_id):
    participated = False
    logfile_dir = "./SpeakerPool/static/studies/" + study_id + "/data/logfiles/"
    try:
        logfiles = [file[:-4] for file in os.listdir(logfile_dir) if file[-4:] == ".txt"]
        for logfile in logfiles:
            if logfile == participant_id:
                participated = True
        return participated
    except:
        return False

def get_completed(study_id, participant_id):
    logfile_path = "./SpeakerPool/static/studies/" + study_id + "/data/logfiles/" + participant_id + ".txt"
    with open(logfile_path, "r") as logfile:
        return len(logfile.readlines())

def get_available(study_id):
    enum_path = "./SpeakerPool/static/studies/" + study_id + "/data/enumeration.txt"
    with open(enum_path, "r", encoding="utf-8") as enumfile:
        return len(enumfile.readlines())

def get_done_prompts(study_id, participant_id, prompts):
    logfile_path = "./SpeakerPool/static/studies/" + study_id + "/data/logfiles/" + participant_id + ".txt"
    done_prompt_ids = []
    if not os.path.isfile(logfile_path):
        open(logfile_path, "w")
    with open(logfile_path, "r") as logfile:
        lines = logfile.readlines()
        for line in lines:
            done_prompt_ids.append(line.split("\t")[0])
    
    return done_prompt_ids

def filter_prompts(all_prompts, done_prompts, prompt_dict):
    prompts = []
    n_removed = 0
    for prompt in all_prompts:
        is_done = False
        for done_prompt in done_prompts:
            if str(prompt_dict[prompt]) == str(done_prompt):
                is_done = True
        if is_done == False:
            prompts.append(prompt)
        else:
            n_removed += 1
    return prompts, n_removed
