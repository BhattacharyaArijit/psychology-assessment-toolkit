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

        self.responses = {}
        self.question_labels = {}
        self.questionnaires = []

        self.question_start_times = {}
        self.response_times = {}

        # Session timer
        self.session_start = time.time()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # App config
        app_conf = config.get("app", {})
        root.title(app_conf.get("title", "Assessment Toolkit"))
        root.geometry(f"{app_conf.get('window_width', 1200)}x{app_conf.get('window_height', 800)}")

        self.output_dir = app_conf.get("output_folder", "output")
        ensure_folder(self.output_dir)

        # Fonts
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

            has_options = any("options" in q for q in qdata.get("questions", []))
            qdata["type"] = "multi_statement" if has_options else "likert"

            if "type" in item:
                qdata["type"] = item["type"]

            qdata["display"] = item.get("display", "horizontal")

            self.questionnaires.append(qdata)


    # Tabs
    def build_tabs(self):
        self.nb = ttk.Notebook(self.root)
        self.nb.pack(fill="both", expand=True)

        for q in self.questionnaires:
            self.build_questionnaire_tab(q)

        # Credits
        for page in self.config.get("credits", []):
            path = os.path.join("credits", f"{page}.json")
            if os.path.exists(path):
                data = load_json(path)
                frame = ttk.Frame(self.nb)
                self.nb.add(frame, text=data.get("title", "Credits"))

                text = "\n".join(data.get("content", []))
                ttk.Label(
                    frame,
                    text=text,
                    wraplength=900,
                    justify="left",
                    font=self.instruction_font
                ).pack(padx=20, pady=20)


    # Questionnaire UI
    def build_questionnaire_tab(self, qdata):
        frame = ttk.Frame(self.nb)
        self.nb.add(frame, text=qdata.get("name", "Questionnaire"))

        # Instructions
        if "instructions" in qdata:
            ttk.Label(
                frame,
                text=qdata["instructions"],
                wraplength=900,
                font=self.instruction_font,
                justify="left"
            ).pack(pady=10)

        # Scrollable area
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
            # Question label
            label_text = q.get("text") or q.get("label", "")
            label_widget = ttk.Label(
                form,
                text=label_text,
                font=self.question_font,
                wraplength=700,
                justify="left",
                background="white"
            )
            label_widget.grid(row=row_pointer, column=0, sticky="w", pady=6)

            # Response setup
            qid = f"{qdata.get('name','Q')}_{q.get('id','')}"
            var = tk.StringVar(value="")

            self.responses[qid] = var
            self.question_labels[qid] = label_widget
            self.question_start_times[qid] = time.time()

            var.trace_add("write", lambda *args, qid=qid: self.on_answer(qid))

            # Options container
            options_frame = ttk.Frame(form)
            options_frame.grid(row=row_pointer + 1, column=0, sticky="w")

            # Render options
            if "options" in q:
                self.render_options(options_frame, q["options"], var, display, is_likert=False)
            else:
                scale = q.get("scale", qdata.get("scale", [1, 2, 3, 4, 5]))
                self.render_options(options_frame, scale, var, display, is_likert=True)

            row_pointer += 2


    # OPTION RENDERING 
    def render_options(self, frame, options, var, display, is_likert):

        max_cols = 5  # for wrapping horizontal layout

        for idx, opt in enumerate(options):

            # Normalize values
            if is_likert:
                if isinstance(opt, dict):
                    value = opt.get("value")
                    text = f"{value} : {opt.get('label','')}"
                else:
                    value = opt
                    text = str(opt)
            else:
                value = opt.get("score")
                text = f"{value} : {opt.get('text','')}"

            rb = tk.Radiobutton(
                frame,
                text=text,
                variable=var,
                value=str(value),
                font=self.option_font,
                anchor="w",
                justify="left",
                wraplength=250 if display == "horizontal" else 700
            )

            if display == "horizontal":
                row = idx // max_cols
                col = idx % max_cols
                rb.grid(row=row, column=col, padx=8, pady=2, sticky="w")
            else:
                rb.pack(anchor="w", pady=2)


    # Tracking
    def on_answer(self, qid):
        self.highlight_question(qid)

        if qid not in self.response_times:
            self.response_times[qid] = round(
                time.time() - self.question_start_times[qid], 2
            )

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

    # Save
    def save_responses(self, status="submitted"):
        end_time = time.time()
        duration = round(end_time - self.session_start, 2)

        sid = self.sid.get().strip() or "UNKNOWN"
        responses_dict = {k: v.get() for k, v in self.responses.items()}

        participant_folder = os.path.join(self.output_dir, sid)
        os.makedirs(participant_folder, exist_ok=True)

        scores_result = calculate_scores(self.questionnaires, responses_dict)

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

        total_row = {
            "SubjectID": sid,
            "Date": self.date.get(),
            "Duration_sec": duration,
            "Status": status
        }

        if isinstance(scores_result, dict) and "totals" in scores_result:
            total_row.update(scores_result["totals"])
        else:
            total_row.update(scores_result)

        total_df = pd.DataFrame([total_row])
        total_df.to_csv(os.path.join(participant_folder, "total.csv"), index=False)

        master_file = os.path.join(self.output_dir, "Master_scores.csv")

        if os.path.exists(master_file):
            total_df.to_csv(master_file, mode="a", header=False, index=False)
        else:
            total_df.to_csv(master_file, index=False)

    # Close
    def on_close(self):
        if messagebox.askyesno("Exit", "Exit assessment? Responses will be saved."):
            self.save_responses(status="cancelled")
            self.root.destroy()
