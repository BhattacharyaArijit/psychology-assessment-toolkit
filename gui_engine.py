import os
import time
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from datetime import datetime

from utils import load_json, ensure_folder
from scorer import calculate_scores


class AssessmentApp:
    def __init__(self, root, config):
        self.root = root
        self.config = config

        self.responses = {}          # QID -> StringVar
        self.question_labels = {}    # QID -> Label widget
        self.questionnaires = []

        self.question_start_times = {}  # QID -> time displayed
        self.response_times = {}        # QID -> time taken

        # Session timer
        self.session_start = time.time()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # App config
        app_conf = config.get("app", {})
        root.title(app_conf.get("title", "Assessment Toolkit"))
        root.geometry(
            f"{app_conf.get('window_width', 1200)}x{app_conf.get('window_height', 800)}"
        )
        self.output_dir = app_conf.get("output_folder", "output")
        ensure_folder(self.output_dir)

        # Font config
        fonts = config.get("fonts", {})
        family = fonts.get("family", "Arial")
        self.question_font = (family, fonts.get("question_size", 12))
        self.option_font = (family, fonts.get("option_size", 11))
        self.instruction_font = (family, fonts.get("instruction_size", 12))

        # Build UI
        self.build_top_bar()
        self.load_questionnaires()
        self.build_tabs()
        ttk.Button(root, text="Submit", command=self.submit).pack(pady=10)

    # Top Bar: Subject ID & Date
    def build_top_bar(self):
        frame = ttk.Frame(self.root)
        frame.pack(pady=10)

        ttk.Label(frame, text="Subject ID").grid(row=0, column=0)
        self.sid = ttk.Entry(frame, width=20)
        self.sid.grid(row=0, column=1, padx=10)

        ttk.Label(frame, text="Date").grid(row=0, column=2)
        self.date = ttk.Entry(frame, width=15)
        self.date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date.grid(row=0, column=3)

    # Load Questionnaires
    def load_questionnaires(self):
        for item in self.config.get("questionnaires", []):
            path = os.path.join("questionnaires", f"{item['file']}.json")
            qdata = load_json(path)

            # Auto-detect type per question
            has_options = any("options" in q for q in qdata.get("questions", []))
            qdata["type"] = "multi_statement" if has_options else "likert"

            # Override with config if explicitly given
            if "type" in item:
                qdata["type"] = item["type"]
            qdata["display"] = item.get("display", "horizontal")

            self.questionnaires.append(qdata)

    # Build Tabs
    def build_tabs(self):
        self.nb = ttk.Notebook(self.root)
        self.nb.pack(fill="both", expand=True)

        for q in self.questionnaires:
            self.build_questionnaire_tab(q)

        # Credits pages
        for page in self.config.get("credits", []):
            path = os.path.join("credits", f"{page}.json")
            if os.path.exists(path):
                data = load_json(path)
                frame = ttk.Frame(self.nb)
                self.nb.add(frame, text=data.get("title", "Credits"))
                text = "\n".join(data.get("content", []))
                ttk.Label(frame, text=text, wraplength=900,
                          justify="left", font=self.instruction_font).pack(padx=20, pady=20)

    # Build Questionnaire Tab
    def build_questionnaire_tab(self, qdata):
        frame = ttk.Frame(self.nb)
        self.nb.add(frame, text=qdata.get("name", "Questionnaire"))

        if "instructions" in qdata:
            ttk.Label(frame, text=qdata["instructions"],
                      wraplength=900, font=self.instruction_font,
                      justify="left").pack(pady=10)

        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        form = ttk.Frame(canvas)
        form.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=form, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        display = qdata.get("display", "horizontal")
        row_pointer = 0

        for q in qdata.get("questions", []):
            label_text = q.get("text") or q.get("label", "")
            label_widget = ttk.Label(form, text=label_text,
                                     font=self.question_font,
                                     wraplength=700, justify="left",
                                     background="white")
            label_widget.grid(row=row_pointer, column=0, sticky="w", pady=6)

            qid = f"{qdata.get('name','Q')}_{q.get('id','')}"
            var = tk.StringVar(value="")
            self.responses[qid] = var
            self.question_labels[qid] = label_widget
            self.question_start_times[qid] = time.time()
            var.trace_add("write", lambda *args, qid=qid: self.on_answer(qid))

            # Determine question type dynamically
            if "options" in q:
                # Multi-statement
                options_frame = ttk.Frame(form)
                options_frame.grid(row=row_pointer + 1, column=0, sticky="w")
                for opt in q["options"]:
                    label_opt = f"{opt.get('score')} : {opt.get('text','')}"
                    tk.Radiobutton(options_frame, text=label_opt,
                                   variable=var, value=opt.get("score"),
                                   font=self.option_font, wraplength=700,
                                   justify="left", anchor="w").pack(anchor="w")
                row_pointer += 2
            else:
                # Likert
                scale = q.get("scale", qdata.get("scale", [1, 2, 3, 4, 5]))
                options_frame = ttk.Frame(form)
                options_frame.grid(row=row_pointer + 1, column=0, sticky="w")
                for val in scale:
                    if isinstance(val, dict):
                        value = val.get("value")
                        label_val = f"{value} : {val.get('label','')}"
                    else:
                        value = val
                        label_val = str(value)
                    tk.Radiobutton(options_frame, text=label_val,
                                   variable=var, value=str(value),
                                   font=self.option_font, anchor="w").pack(anchor="w")
                row_pointer += 2

    # Track Answer Time & Highlight
    def on_answer(self, qid):
        self.highlight_question(qid)
        if qid not in self.response_times:
            self.response_times[qid] = round(time.time() - self.question_start_times[qid], 2)

    def highlight_question(self, qid):
        label_widget = self.question_labels.get(qid)
        if label_widget:
            label_widget.configure(background="#ccffcc")

    # Submit
    def submit(self):
        if not self.sid.get().strip():
            messagebox.showwarning("Missing", "Please enter Subject ID")
            return
        self.save_responses(status="submitted")
        messagebox.showinfo("Saved", "Responses saved successfully")
        self.root.destroy()

    # Save Responses
    def save_responses(self, status="submitted"):
        end_time = time.time()
        duration = round(end_time - self.session_start, 2)
        sid = self.sid.get().strip() or "UNKNOWN"
        responses_dict = {k: v.get() for k, v in self.responses.items()}

        participant_folder = os.path.join(self.output_dir, sid)
        os.makedirs(participant_folder, exist_ok=True)

        scores_result = calculate_scores(self.questionnaires, responses_dict)

        # Flexible handling: items if available
        all_data = []
        if isinstance(scores_result, dict) and "items" in scores_result:
            for qid, val_dict in scores_result["items"].items():
                all_data.append({
                    "SubjectID": sid,
                    "Date": self.date.get(),
                    "Question": qid,
                    "Raw": val_dict.get("raw"),
                    "ReverseCoded": val_dict.get("score"),
                    "ResponseTime_sec": self.response_times.get(qid)
                })
        else:
            # fallback: raw responses only
            for qid, raw in responses_dict.items():
                all_data.append({
                    "SubjectID": sid,
                    "Date": self.date.get(),
                    "Question": qid,
                    "Raw": raw,
                    "ReverseCoded": raw,
                    "ResponseTime_sec": self.response_times.get(qid)
                })

        all_df = pd.DataFrame(all_data)
        all_df["Status"] = status
        all_df["TotalDuration_sec"] = duration
        all_df.to_csv(os.path.join(participant_folder, "all_questions.csv"), index=False)

        # Save totals
        total_row = {"SubjectID": sid, "Date": self.date.get(),
                     "Duration_sec": duration, "Status": status}
        if isinstance(scores_result, dict) and "totals" in scores_result:
            total_row.update(scores_result["totals"])
        else:
            total_row.update(scores_result)

        total_df = pd.DataFrame([total_row])
        total_df.to_csv(os.path.join(participant_folder, "total.csv"), index=False)

        # Update master file
        master_file = os.path.join(self.output_dir, "Master_scores.csv")
        if os.path.exists(master_file):
            total_df.to_csv(master_file, mode="a", header=False, index=False)
        else:
            total_df.to_csv(master_file, index=False)

    # On Window Close 
    def on_close(self):
        if messagebox.askyesno("Exit", "Exit assessment? Responses will be saved."):
            self.save_responses(status="cancelled")
            self.root.destroy()
