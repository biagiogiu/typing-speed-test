from tkinter import Tk, Frame, messagebox, Label, Button, Entry, RIDGE, FLAT, Text, StringVar, IntVar
import pandas as pd

try:
    with open('scores.csv', 'r') as f:
        scores = pd.read_csv(f)
except FileNotFoundError:
    with open('scores.csv', 'w') as f:
        scores = pd.DataFrame(columns=["name", "lpm", "precision"])
        scores.to_csv('scores.csv', index=False)

player = ""
new_score = None


class SpeedTest(Tk):
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.title('Typing Speed Test')
        container = Frame(self)
        container.pack(side="top", fill="both", expand=True, padx=10, pady=10)
        self.frames = {}

        for F in (StartPage, Test, Score):
            frame = F(parent=container, controller=self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.go_to(StartPage)

    def go_to(self, page):
        frame = self.frames[page]
        frame.tkraise()

    def start(self):
        name = self.frames[StartPage].e_name.get()
        if name == "":
            messagebox.showwarning(title="Name missing", message="Please type your name")
        else:
            global player
            player = name
            self.frames[Test].text_box.focus_set()
            self.frames[Test].reposition_cursor(None)
            self.go_to(Test)


class StartPage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.container = Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.columnconfigure(0, weight=1)
        self.container.columnconfigure(1, weight=1)
        self.l_name = Label(self.container, text="Your name:")
        self.l_name.grid(row=0, column=0, sticky='e', padx=10, pady=10)

        self.f_name = Frame(self.container, width=50, relief=RIDGE, borderwidth=2)
        self.f_name.grid(row=0, column=1, sticky='w', padx=10, pady=10)
        self.e_name = Entry(self.f_name, borderwidth=5, relief=FLAT)
        self.e_name.pack()

        self.b_start = Button(self.container, text="Start", width=15, padx=2, command=lambda: app.start())
        self.b_start.grid(row=1, column=0, columnspan=2, pady=10)

        self.b_score = Button(self.container, text="Scores", width=15, padx=2, command=lambda: app.go_to(Score))
        self.b_score.grid(row=2, column=0, columnspan=2, pady=10)


class Test(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)

        with open("Text.txt", "r", encoding="utf8") as file:
            self.text = file.read()
        self.length = len(self.text)
        self.cursor = 0
        self.error_no = IntVar(self, 0)
        self.time = 0
        self.formatted_time = StringVar(self)
        self.formatted_time.set(self.format_time(self.time))
        self.timer_sec = None
        self.lpm = IntVar(self, 0)

        self.container = Frame(self, relief=RIDGE, borderwidth=2, width=1080, height=630)
        self.text_box = Text(self.container, padx=10, pady=10)
        self.text_box.insert(1.0, self.text)
        self.text_box.bind("<Key>", self.check_char)
        self.text_box.bind("Control-Return", self.check_char)
        self.text_box.bind("<ButtonRelease>", self.reposition_cursor)
        self.text_box.tag_config("green", foreground="green")
        self.text_box.tag_config("red", foreground="red")

        bar = Frame(self, height=30)
        error_l = Label(bar, text="Typos:")
        error_no_l = Label(bar, width=3, textvariable=self.error_no)
        time_l = Label(bar, text="Time:")
        seconds_l = Label(bar, width=3, textvariable=self.formatted_time)
        lpm_l = Label(bar, text="Letters/min:")
        lpm_no_l = Label(bar, textvariable=self.lpm)
        self.scores = Button(bar, text="Scores", command=self.reset_and_go_to_scores)

        self.container.pack(fill="both", expand=True)
        self.text_box.pack()
        bar.pack(side="bottom", fill="x", expand=True, padx=10, pady=10)
        error_l.pack(side='left', padx=5)
        error_no_l.pack(side='left', padx=5)
        time_l.pack(side='left', padx=(20, 5))
        seconds_l.pack(side='left', padx=5)
        lpm_l.pack(side='left', padx=(20, 5))
        lpm_no_l.pack(side='left', padx=5)

    def check_char(self, event):
        if event.char == '\x08':
            return 'break'
        elif event.char != '':
            if self.time == 0:
                self.run_timer()
            if event.char == self.text[self.cursor]:
                if "red" not in self.text_box.tag_names("%d.%d" % (1, self.cursor)):
                    self.text_box.delete("%d.%d" % (1, self.cursor))
                    self.text_box.insert("%d.%d" % (1, self.cursor), self.text[self.cursor])
                    self.text_box.tag_add("green", "%d.%d" % (1, self.cursor-1), "%d.%d" % (1, self.cursor+1))
                if self.cursor == self.length - 1:
                    self.end_test()
                    return 'break'
                self.cursor += 1
                self.reposition_cursor(event)
                return 'break'
            else:
                if "red" not in self.text_box.tag_names("%d.%d" % (1, self.cursor)):
                    self.text_box.tag_add("red", "%d.%d" % (1, self.cursor), "%d.%d" % (1, self.cursor + 1))
                    self.error_no.set(self.error_no.get() + 1)
                return 'break'

    def run_timer(self):
        self.time += 100
        if self.time % 1000 == 0:
            self.formatted_time.set(self.format_time(self.time))
        self.update_lpm()
        self.timer_sec = app.after(100, self.run_timer)

    def reposition_cursor(self, event):
        self.text_box.mark_set("insert", "%d.%d" % (1, self.cursor))
        return 'break'

    def format_time(self, time):
        mins, secs = divmod(time // 1000, 60)
        return '{:02d}:{:02d}'.format(mins, secs)

    def update_lpm(self):
        if self.time != 0:
            self.lpm.set((self.cursor + 1) * 60000 // self.time)

    def end_test(self):
        self.text_box['state'] = 'disabled'
        app.after_cancel(self.timer_sec)
        self.scores.pack(side='right', padx=5)

    def reset_and_go_to_scores(self):
        self.save_score()
        self.text_box['state'] = 'normal'
        self.time = 0
        self.lpm.set(0)
        self.cursor = 0
        self.scores.pack_forget()
        for tag in self.text_box.tag_names():
            self.text_box.tag_delete(tag)
        self.text_box.tag_config("green", foreground="green")
        self.text_box.tag_config("red", foreground="red")
        global new_score
        new_score = None
        app.frames[Score].refresh_scores()
        app.go_to(Score)

    def save_score(self):
        global new_score
        precision = round(100 - (self.error_no.get() * 100 / len(self.text)), 1)
        new_score = {'name': player,
                     'lpm': self.lpm.get(),
                     'precision': f"{precision}%"}
        global scores
        scores.loc[scores.index.max() + 1] = new_score
        scores = scores.sort_values(['lpm', 'precision'], ascending=[False, True])
        scores.reset_index(inplace=True, drop=True)
        scores = scores.head(10)
        scores.to_csv('scores.csv', index=False)


class Score(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.container = Frame(self)
        self.container.pack(side='top', fill='both', expand=True)
        self.l_score = Label(self.container, text="Top 10 scores")
        self.l_score.pack(pady=(10, 20))
        self.table = Frame(self.container)
        self.table.pack(fill="x", expand=True, padx=10, pady=10)
        self.table.columnconfigure(0, weight=2)
        self.table.columnconfigure(1, weight=1)
        self.table.columnconfigure(2, weight=2)
        self.b_start = Button(self.container, text="New speed test", height=2, command=lambda: app.go_to(StartPage))
        self.b_start.pack(fill="x", side="bottom", expand=True, padx=10, pady=10)
        self.refresh_scores()

    def refresh_scores(self):
        no_scores = Label(self.table, text="No scores available")
        if scores.size == 0:
            no_scores.grid(row=0, column=0, columnspan=2, sticky="we")
        else:
            if self.table.winfo_children():
                for child in self.table.winfo_children():
                    child.destroy()
            name = Label(self.table, text=scores.columns[0].title())
            name.grid(row=0, column=0, padx=(0, 5), pady=(0, 10), sticky="e")
            score = Label(self.table, text=scores.columns[1].upper())
            score.grid(row=0, column=1, padx=5, pady=(0, 10), sticky="ew")
            precision_l = Label(self.table, text=scores.columns[2].title())
            precision_l.grid(row=0, column=2, padx=(5, 0), pady=(0, 10), sticky="w")

            for x in range(scores['name'].size):
                name = scores['name'][x]
                label_name = Label(self.table, text=name)
                label_name.grid(row=x + 1, column=0, padx=(0, 5), pady=1, sticky="e")
                score = scores['lpm'][x]
                label_score = Label(self.table, text=score)
                label_score.grid(row=x + 1, column=1, padx=5, pady=1, sticky="ew")
                precision = scores['precision'][x]
                label_precision = Label(self.table, text=precision)
                label_precision.grid(row=x + 1, column=2, padx=(5, 0), pady=1, sticky="w")
                if (new_score and scores['name'][x] == new_score['name'] and scores['lpm'][x] == new_score['lpm'] and
                        scores['precision'][x] == new_score['precision']):
                    label_name.config(foreground='red')
                    label_score.config(foreground='red')
                    label_precision.config(foreground='red')


app = SpeedTest()

app.mainloop()
