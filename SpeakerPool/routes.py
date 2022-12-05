from flask import render_template, url_for, request, redirect, session, flash
from SpeakerPool.forms import RegistrationForm, LoginForm, ConsentForm, EmailForm
from SpeakerPool.models import Account, StudyEntry
import SpeakerPool.utils as ut
from SpeakerPool import app, db, bcrypt
from flask_login import login_user, current_user, logout_user

import json, os, librosa, random

@app.route('/')
def find_path():
    return redirect(url_for("home", lang="eng"))

@app.route('/hackyupload', methods=['GET', 'POST'])
def hackyupload():
    if request.method == "POST":
        print(request.form["filename"])
        print(request.form["data"])
        with open(request.form["filename"], "w") as f:
            f.write(request.form["data"]) 
    return "hackity hack hack uploaded"

@app.route('/-<lang>')
def home(lang):
    studies_list = ut.get_study_dict()
    for study in studies_list:
        study["total_recording"] = round(study["total_recording"], 2)
    if current_user.is_authenticated:
        for study in studies_list:
            participated = ut.check_for_participation(str(study["id"]), str(current_user.id))
            if participated:

                ut.gen_prompt_dict(study["id"])
            
                # TODO move this to be created when the study is first generated
                # dict_filepath = "./SpeakerPool/static/studies/" + str(study["id"]) + "/data/enumeration.txt"
                # if not os.path.isfile(dict_filepath):
                #     with open(dict_filepath, "a") as dict_file:
                #         for key in list(prompt_dict.keys()):
                #             prompt_line = str(prompt_dict[key]) + "\t" + str(key) + "\n"
                #             dict_file.write(prompt_line)
                ####################################################################
                study["participated"] = "True"
                study["completed"] = ut.get_completed(str(study["id"]), str(current_user.id))
                study["available"] = ut.get_available(str(study["id"]))
            else:
                study["participated"] = "False"
    return render_template("home.html", studies_list=studies_list, lang=lang)

@app.route('/register-<lang>', methods=['GET', 'POST'])
def register(lang):
    if current_user.is_authenticated:
        return redirect(url_for("home", lang=lang))
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = Account(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        with open(r"SpeakerPool/static/translations.json", "r") as translations_file:
            translations = json.load(translations_file)
            flash(translations['successfulsignin'][lang], "success")
        return redirect(url_for('login', lang=lang))
    return render_template("register.html", form=form, lang=lang)

@app.route('/login-<lang>', methods=['GET', 'POST'])
def login(lang):
    if current_user.is_authenticated:
        return redirect(url_for("home", lang=lang))
    form = LoginForm()
    if form.validate_on_submit():
        user = Account.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            with open(r"SpeakerPool/static/translations.json", "r") as translations_file:
                translations = json.load(translations_file)
                message = translations['welcome'][lang] + " " + form.username.data + "."
                flash(message, "success")
            try:
                if session['url'] is not None:
                    return redirect(session['url'])
                return redirect(url_for('home', lang=lang))
            except KeyError:
                return redirect(url_for("home", lang=lang))
        else:
            with open(r"SpeakerPool/static/translations.json", "r") as translations_file:
                translations = json.load(translations_file)
                flash(translations['invalidlogin'][lang], "danger")
    return render_template("login.html", form=form, lang=lang)

@app.route('/logout-<lang>')
def logout(lang):
    # check if logged in
    if not current_user.is_authenticated:
        return redirect(url_for('login', lang=lang))
    logout_user()
    with open(r"SpeakerPool/static/translations.json", "r") as translations_file:
        translations = json.load(translations_file)
        flash(translations['signedout'][lang], "success")
    return redirect(url_for('home', lang=lang))

@app.route('/account-<lang>')
def account(lang):
    # check if logged in
    if not current_user.is_authenticated:
        session['url'] = url_for('account', lang=lang)
        return redirect(url_for('login', lang=lang))
    return render_template('account.html', lang=lang)
    
@app.route('/info-<lang>')
def info(lang):
    return render_template('info.html', lang=lang)

@app.route('/consent/<study_id>-<lang>', methods=['GET', 'POST'])
def consent(study_id, lang):
    # check if logged in
    if not current_user.is_authenticated:
        session['url'] = url_for('consent', study_id=study_id, lang=lang)
        return redirect(url_for('login', lang=lang))
    form = ConsentForm()
    if form.validate_on_submit():
        filename = r"./SpeakerPool/static/studies/"+str(study_id)+"/data/demographic/"+str(current_user.id)+".txt"
        # check if there is already a demographic file with consent information
        if not os.path.isfile(filename):
            print(filename)
            with open(filename, "a") as f: # save responses to a file
                line = "Consent Received\tTrue\n"
                f.write(line)
        return redirect(url_for('email', study_id=study_id, lang=lang))
    return render_template("consent.html", study_id=study_id, study_name=ut.get_studyname(study_id), form=form, lang=lang)
    
@app.route('/email/<study_id>-<lang>', methods=['GET', 'POST'])
def email(study_id, lang):
    # check if logged in
    if not current_user.is_authenticated:
        session['url'] = url_for('consent', study_id=study_id, lang=lang)
        return redirect(url_for('login', lang=lang))
    user = Account.query.filter_by(id=current_user.id).first()
    email = user.email
    if email != None:
        return redirect(url_for('demographic', study_id=study_id, lang=lang))
    form = EmailForm()
    if form.validate_on_submit():
        email_address = form.email.data
        user.email = email_address
        db.session.commit()
        print(email_address)
        return redirect(url_for('demographic', study_id=study_id, lang=lang))
    return render_template("email.html", study_id=study_id, form=form, lang=lang)

@app.route('/demographic/<study_id>-<lang>', methods=['GET', 'POST'])
def demographic(study_id, lang):
    # check if logged in
    if not current_user.is_authenticated:
        session['url'] = url_for('demographic', study_id=study_id, lang=lang)
        return redirect(url_for('login', lang=lang))
    filename = r"./SpeakerPool/static/studies/"+str(study_id)+"/data/demographic/"+str(current_user.id)+".txt"
    # check if there is already a demographic file with consent information
    if not os.path.isfile(filename):
        return redirect(url_for('consent', study_id=study_id, lang=lang))
    # check if the participant has already filled out the demographic information for this study
    if ut.done_demographic(study_id, current_user):
        return redirect(url_for('instructions', study_id=study_id, lang=lang)) 
    return render_template("demographic.html", demographic_dict=ut.get_demographic(study_id), study_id=study_id, study_name=ut.get_studyname(study_id), lang=lang)

@app.route('/datareception/<study_id>-<lang>', methods=['GET', 'POST'])
def datareception(study_id, lang):
    if request.method == "POST":
        print("found post request")
        filename = r"./SpeakerPool/static/studies/"+str(study_id)+"/data/demographic/"+str(current_user.id)+".txt"
        if not ut.done_demographic(study_id, current_user):
            print("notdone")
            with open(filename, "a") as f: # save responses to a file
                print(filename)
                print(request.form.items())
                for item in request.form.items():
                    line = item[0] + "\t" + item[1] + "\n"
                    print(item)
                    f.write(line)
    return redirect(url_for("instructions", study_id=study_id, lang=lang))

@app.route('/instructions/<study_id>-<lang>')
def instructions(study_id, lang):
    # check if logged in
    if not current_user.is_authenticated:
        session['url'] = url_for('instructions', study_id=study_id, lang=lang)
        return redirect(url_for('login', lang=lang))
    filename = r"./SpeakerPool/static/studies/"+str(study_id)+"/data/demographic/"+str(current_user.id)+".txt"
    # check if there is already a demographic file with consent information
    if not os.path.isfile(filename):
        return redirect(url_for('consent', study_id=study_id, lang=lang))
    # check if the participant has already filled out demographic information for this study
    if not ut.done_demographic(study_id, current_user):
        return redirect(url_for('demographic', study_id=study_id, lang=lang))
    return render_template("instructions.html", study_id=study_id, study_name=ut.get_studyname(study_id), lang=lang)

@app.route('/study/<study_id>-<lang>', methods=['GET', 'POST'])
def study(study_id, lang):
    # check if logged in
    if not current_user.is_authenticated:
        session['url'] = url_for('study', study_id=study_id, lang=lang)
        return redirect(url_for('login', lang=lang))
    filename = r"./SpeakerPool/static/studies/"+str(study_id)+"/data/demographic/"+str(current_user.id)+".txt"
    # check if there is already a demographic file with consent information
    if not os.path.isfile(filename):
        return redirect(url_for('consent', study_id=study_id, lang=lang))
    if not ut.done_demographic(study_id, current_user):
        return redirect(url_for('demographic', study_id=study_id, lang=lang))

    prompt_dict = ut.gen_prompt_dict(study_id)

    # TODO move this to be created when the study is first generated
    # dict_filepath = "./SpeakerPool/static/studies/" + str(study_id) + "/data/enumeration.txt"
    # if not os.path.isfile(dict_filepath):
    #     with open(dict_filepath, "a") as dict_file:
    #         for key in list(prompt_dict.keys()):
    #             prompt_line = str(prompt_dict[key]) + "\t" + str(key) + "\n"
    #             dict_file.write(prompt_line)
    ####################################################################
    
    # account for randomize and already done prompts
    filename = r"./SpeakerPool/static/studies/" + study_id + r"/prompts.txt"
    file = open(filename, "r", encoding="cp1252")
    all_prompts = [x.strip("\n") for x in file.readlines()] 
    random_selected = False
    for i in range(len(all_prompts)):
        if all_prompts[i] == "RANDOMIZE":
            ordered = all_prompts[:i]
            randomized = all_prompts[i+1:]
            random.shuffle(randomized)
            random_selected = True
    if random_selected:
        all_prompts = ordered + randomized

    done_prompts = ut.get_done_prompts(str(study_id), str(current_user.id), all_prompts)
    prompts, n_removed = ut.filter_prompts(all_prompts, done_prompts, prompt_dict)
    while n_removed > 0:
        prompts, n_removed = ut.filter_prompts(prompts, done_prompts, prompt_dict)

    if len(prompts) <= 0:
        return redirect(url_for("complete", lang=lang))

    participant_num = str(current_user.id)
    # SAVING RECORDING
    if request.method == "POST":
        current_study = StudyEntry.query.get(study_id)
        prompt_id = prompt_dict[request.form["prompt"]]
        participant_num = str(current_user.id)
        wav_filename = "./SpeakerPool/static/studies/" + str(study_id) + "/data/recordings/" + participant_num + "_" + str(prompt_id) + ".wav"
        log_filepath = "./SpeakerPool/static/studies/" + str(study_id) + "/data/logfiles/" + participant_num + ".txt"
        # if they haven't yet done a prompt update the number of participants in db
        if ut.get_completed(study_id, participant_num) == 0:
            current_study.n_participants += 1
        logfile = open(log_filepath, "a")
        if request.form["samplerate"] == "SKIPPED":
            wav_basename = "SKIPPED"
        else:
            request.files["recording"].save(wav_filename)
            wav_basename = os.path.basename(wav_filename)
            current_study.n_recordings += 1
            seconds_len = librosa.get_duration(filename=wav_filename)
            minutes_len = seconds_len / 60
            hours_len = minutes_len / 60
            current_study.total_recording += hours_len
        mic = str(request.form["mic"])
        if mic == "":
            mic = "UNKNOWN"
        entry = "%s\t%s\t%s\t%s\n" % (str(prompt_id), str(request.form["samplerate"]), mic, wav_basename)
        logfile.write(entry)
        logfile.close()
        db.session.commit()

    return render_template("study.html", prompts=json.dumps(prompts), study_id=str(study_id), study_name=ut.get_studyname(study_id), lang=lang)

@app.route('/complete-<lang>')
def complete(lang):
    return render_template('complete.html', lang=lang)

# @app.route('/recognition-<lang>')
# def recognition(lang):
#     return render_template('recognition.html', lang=lang)
