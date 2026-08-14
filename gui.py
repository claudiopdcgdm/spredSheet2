import os
import threading
import logging
import tkinter as tk

from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText

from dotenv import load_dotenv

import inbound
import outbound
import scheduller
import config
from datetime import datetime
from logger import logger

VERSION = "5.0.0"
BUILD_DATE = "13/08/2026"

load_dotenv()


# ==========================================================
# HANDLER DO TKINTER
# ==========================================================

class TkinterLogHandler(logging.Handler):

    def __init__(self, text_widget):

        super().__init__()

        self.text_widget = text_widget


    def emit(self, record):

        try:

            mensagem = self.format(record)

            # O Tkinter precisa ser atualizado pela
            # thread principal
            self.text_widget.after(
                0,
                self._append_log,
                mensagem
            )

        except Exception:

            pass


    def _append_log(self, mensagem):

        try:

            self.text_widget.config(
                state="normal"
            )

            self.text_widget.insert(
                tk.END,
                mensagem + "\n"
            )

            self.text_widget.see(
                tk.END
            )

            self.text_widget.config(
                state="disabled"
            )

        except Exception:

            pass


# ==========================================================
# APLICAÇÃO
# ==========================================================

class Application:

    def open_config_window(self):

        window = tk.Toplevel(self.root)

        window.title(
            "Configurações"
        )

        window.geometry(
            "600x500"
        )

        window.resizable(
            False,
            False
        )

        window.transient(
            self.root
        )

        window.grab_set()


        # ======================================================
        # CAMPOS
        # ======================================================

        fields = [
            (
                "Planilha Recebimento",
                "SPREDSHEET_REC"
            ),
            (
                "Planilha Devolução",
                "SPREDSHEET_DEV"
            ),
            (
                "Nome Base BI",
                "SHEET_NAME_BASE_BI"
            ),
            (
                "Tempo Recebimento (horas)",
                "TIME_UPDATE_JOB_RECEB"
            ),
            (
                "Tempo Base BI (minutos)",
                "TIME_UPDATE_JOB_BASE"
            ),
            (
                "Dias Limite Devolução",
                "DAYS_LIMIT_DEV"
            ),
            (
                "Dias Limite Recebimento",
                "DAYS_LIMIT_RECEB"
            )
        ]


        entries = {}


        for row, (label, key) in enumerate(fields):

            ttk.Label(
                window,
                text=label
            ).grid(
                row=row,
                column=0,
                padx=15,
                pady=10,
                sticky="w"
            )


            entry = ttk.Entry(
                window,
                width=50
            )

            entry.grid(
                row=row,
                column=1,
                padx=15,
                pady=10
            )


            value = os.getenv(
                key,
                ""
            )


            entry.insert(
                0,
                value
            )


            entries[key] = entry


    # ======================================================
    # SALVAR
    # ======================================================

        def save():
            try:
                values = {}
                for key, entry in entries.items():

                    value = entry.get().strip()

                    if not value:

                        messagebox.showwarning(
                            "Configuração",
                            f"O campo {key} não pode ficar vazio."
                        )

                        return

                    values[key] = value


                config.configuration(
                    values["SPREDSHEET_REC"],
                    values["SPREDSHEET_DEV"],
                    values["SHEET_NAME_BASE_BI"],
                    values["TIME_UPDATE_JOB_RECEB"],
                    values["TIME_UPDATE_JOB_BASE"],
                    values["DAYS_LIMIT_DEV"],
                    values["DAYS_LIMIT_RECEB"]
                )


                load_dotenv(
                    override=True
                )


                logger.info(
                    "Configurações salvas com sucesso. Reinicie a aplicação"
                )


                messagebox.showinfo(
                    "Configurações",
                    "Configurações salvas com sucesso, Reinicie a aplicação"
                )
                window.destroy()
            except Exception:
                logger.exception(
                    "Erro ao salvar configurações."
                )
                messagebox.showerror(
                    "Erro",
                    "Não foi possível salvar as configurações."
                )


    # ======================================================
    # BOTÕES
    # ======================================================

        frame_buttons = ttk.Frame(
            window
        )

        frame_buttons.grid(
            row=len(fields),
            column=0,
            columnspan=2,
            pady=25
        )


        ttk.Button(
            frame_buttons,
            text="Salvar",
            command=save
        ).pack(
            side="left",
            padx=10
        )


        ttk.Button(
            frame_buttons,
            text="Cancelar",
            command=window.destroy
        ).pack(
            side="left",
            padx=10
        )


    # def stop_scheduler(self):

    #     if not self.scheduler_running:

    #         logger.warning(
    #             "Scheduler não está em execução."
    #         )

    #         return


    #     logger.info(
    #         "Solicitando parada da automação..."
    #     )


    #     try:

    #         scheduller.stop()


    #         self.scheduler_running = False


    #         self.status_label.config(
    #             text="Automação parada"
    #         )


    #         self.btn_start.config(
    #             state="normal"
    #         )


    #         self.btn_stop.config(
    #             state="disabled"
    #         )


    #         logger.info(
    #             "Automação parada com sucesso."
    #         )


    #     except Exception:

    #         logger.exception(
    #             "Erro ao parar Scheduler."
    #         )
        
    def __init__(self, root):

        self.root = root

        self.root.title(
            "Automação de Dados Reversa"
        )

        self.root.geometry(
            "750x600"
        )

        self.root.resizable(
            False,
            False
        )

        self.scheduler_running = False

        self.create_interface()

        self.configure_logger()

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.close
        )


    # ======================================================
    # INTERFACE
    # ======================================================

    def create_interface(self):

        # ======================================================
        # FOOTER
        # ======================================================

        frame_footer = ttk.Frame(
            self.root,
            padding=(20, 5)
        )

        frame_footer.pack(
            fill="x",
            side="bottom"
        )


        footer_label = ttk.Label(
            frame_footer,
            text=f"Version: {VERSION}   |   Data: {BUILD_DATE}",
            font=("Arial", 8)
        )

        footer_label.pack(
            anchor="e"
        )
        # --------------------------------------------------
        # HEADER
        # --------------------------------------------------

        frame_header = ttk.Frame(
            self.root,
            padding=20
        )

        frame_header.pack(
            fill="x"
        )


        title = ttk.Label(
            frame_header,
            text="Automação de Dados Reversa",
            font=("Arial", 20, "bold")
        )

        title.pack()


        developer = ttk.Label(
            frame_header,
            text="Developer By Claudião",
            font=("Arial", 9)
        )

        developer.pack(
            pady=(5, 0)
        )


        # --------------------------------------------------
        # STATUS
        # --------------------------------------------------

        frame_status = ttk.LabelFrame(
            self.root,
            text="Status",
            padding=10
        )

        frame_status.pack(
            fill="x",
            padx=20,
            pady=10
        )


        self.status_label = ttk.Label(
            frame_status,
            text="Automação parada",
            font=("Arial", 11, "bold"),
            foreground="red"
        )

        self.status_label.pack(
            anchor="w"
        )


        # --------------------------------------------------
        # PROCESSOS
        # --------------------------------------------------

        frame_buttons = ttk.LabelFrame(
            self.root,
            text="Processos",
            padding=15
        )

        frame_buttons.pack(
            fill="x",
            padx=20,
            pady=10
        )


        # Iniciar automação

        self.btn_start = ttk.Button(
            frame_buttons,
            text="▶  Iniciar Automação",
            command=self.start_scheduler
        )

        self.btn_start.pack(
            fill="x",
            pady=5
        )
        # self.btn_stop = ttk.Button(
        #     frame_buttons,
        #     text="■  Parar Automação",
        #     command=self.stop_scheduler,
        #     state="disabled"
        # )

        # self.btn_stop.pack(
        #     fill="x",
        #     pady=5
        # )


        # Inbound

        self.btn_inbound = ttk.Button(
            frame_buttons,
            text="↓  Executar Inbound (Recebimento)",
            command=self.run_inbound
        )

        self.btn_inbound.pack(
            fill="x",
            pady=5
        )


        # Outbound

        self.btn_outbound = ttk.Button(
            frame_buttons,
            text="↑  Executar Outbound",
            command=self.run_outbound
        )

        self.btn_outbound.pack(
            fill="x",
            pady=5
        )


        # Configurações

        self.btn_config = ttk.Button(
            frame_buttons,
            text="⚙  Configurações",
            command=self.run_config
        )

        self.btn_config.pack(
            fill="x",
            pady=5
        )


        # --------------------------------------------------
        # LOG
        # --------------------------------------------------

        frame_log = ttk.LabelFrame(
            self.root,
            text="Log",
            padding=10
        )

        frame_log.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(5, 20)
        )


        self.log_text = ScrolledText(
            frame_log,
            height=12,
            state="disabled",
            font=("Consolas", 9)
        )

        self.log_text.pack(
            fill="both",
            expand=True
        )

       
    # ======================================================
    # CONFIGURA LOGGER
    # ======================================================

    def configure_logger(self):

        self.log_handler = TkinterLogHandler(
            self.log_text
        )


        self.log_handler.setLevel(
            logging.INFO
        )


        self.log_handler.setFormatter(
            logging.Formatter(
                "[%(asctime)s] %(levelname)s - %(message)s",
                datefmt="%H:%M:%S"
            )
        )


        logger.addHandler(
            self.log_handler
        )


        logger.info(
            "Interface iniciada."
        )


    # ======================================================
    # SCHEDULER
    # ======================================================

    def start_scheduler(self):

        if self.scheduler_running:

            logger.warning(
                "Scheduler já está em execução."
            )

            return


        self.scheduler_running = True


        self.status_label.config(
            text="Automação em execução",
            foreground="green"
        )


        self.btn_start.config(
            state="disabled"
        )

        # self.btn_stop.config(
        #     state="normal"
        # )

        logger.info(
            "Iniciando scheduler..."
        )


        thread = threading.Thread(
            target=self._scheduler_thread,
            daemon=True
        )

        thread.start()


    def _scheduler_thread(self):

        try:

            scheduller.start()

            logger.info(
                "Scheduler iniciado com sucesso."
            )

        except Exception:

            logger.exception(
                "Erro no scheduler."
            )

        finally:

            self.scheduler_running = False


            self.root.after(
                0,
                lambda: self.status_label.config(
                    text="Automação parada",
                    foreground="red"
                )
            )


            self.root.after(
                0,
                lambda: self.btn_start.config(
                    state="normal"
                )
            )

            # self.root.after(
            #     0,
            #     lambda: self.btn_stop.config(
            #         state="disabled"
            #     )
            # )


    # ======================================================
    # INBOUND
    # ======================================================

    def run_inbound(self):

        logger.info(
            "Iniciando processo Inbound..."
        )


        thread = threading.Thread(
            target=self._inbound_thread,
            daemon=True
        )

        thread.start()


    def _inbound_thread(self):

        try:

            spreadsheet_id = os.getenv(
                "SPREDSHEET_REC"
            )


            if not spreadsheet_id:

                raise Exception(
                    "SPREDSHEET_REC não configurado."
                )


            inbound.run(
                spreadsheet_id
            )


            logger.info(
                "Processo Inbound finalizado."
            )


        except Exception:

            logger.exception(
                "Erro no processo Inbound."
            )


    # ======================================================
    # OUTBOUND
    # ======================================================

    def run_outbound(self):

        logger.info(
            "Iniciando processo Outbound..."
        )


        thread = threading.Thread(
            target=self._outbound_thread,
            daemon=True
        )

        thread.start()


    def _outbound_thread(self):

        try:

            outbound.run()


            logger.info(
                "Processo Outbound finalizado."
            )


        except Exception:

            logger.exception(
                "Erro no processo Outbound."
            )


    # ======================================================
    # CONFIGURAÇÕES
    # ======================================================
    def run_config(self):

      logger.info(
        "Abrindo configurações..."
      )

      self.open_config_window()

   
    def _config_thread(self):

        try:

            config.configuration()


            # Recarrega o .env
            load_dotenv(
                override=True
            )


            logger.info(
                "Configurações atualizadas."
            )


        except Exception:

            logger.exception(
                "Erro nas configurações."
            )


    # ======================================================
    # FECHAR
    # ======================================================

    def close(self):

        resposta = messagebox.askyesno(
            "Sair",
            "Deseja realmente sair?"
        )


        if not resposta:

            return


        logger.info(
            "Encerrando aplicação..."
        )


        try:

            if self.scheduler_running:

                logger.info(
                    "Encerrando scheduler..."
                )


                scheduller.scheduler.shutdown(
                    wait=False
                )


        except Exception:

            pass


        try:

            logger.removeHandler(
                self.log_handler
            )

        except Exception:

            pass


        self.root.destroy()