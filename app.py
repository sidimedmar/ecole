import streamlit as st
import pandas as pd
import json
import os
import time
from datetime import datetime

# --- CONFIGURATION DES FICHIERS ---
DB_TESTS = "tests_data.json"
DB_STUDENTS = "students_list.json"
DB_RESULTS = "quiz_results.json"
TEACHER_PIN = "1234" 

# --- TRADUCTIONS ---
LANGS = {
    "Français": {
        "dir": "ltr",
        "prof_space": "👨‍🏫 Espace Enseignant",
        "student_space": "🎓 Espace Élève",
        "tabs": ["📝 Créer Test", "👥 Classes", "📊 Résultats", "📜 Historique", "⚙️ Paramètres"],
        "q_label": "Question à poser",
        "q_ans": "Réponses attendues (pour le score auto)",
        "add_q": "➕ Ajouter la question au test",
        "save_test": "💾 Publier le Test pour les élèves",
        "res_title": "Réponses des élèves à corriger",
        "hist_title": "Historique des notes",
        "note_label": "Attribuer une note /20",
        "tel_label": "Sélectionne ton numéro de téléphone",
        "nom_label": "Saisis ton Nom complet",
        "start_exam": "🚀 DÉMARRER LE TEST",
        "time_rem": "Temps restant",
        "send": "Envoyer ma réponse au professeur",
        "finish": "✅ Tes réponses ont été envoyées avec succès !",
        "no_test": "Aucun test disponible actuellement.",
        "import_btn": "Importer la liste des élèves",
        "class_label": "Choisis ta Classe",
        "reset_btn": "🗑️ Réinitialiser tout",
        "rep_label": "Ta réponse :"
    },
    "العربية": {
        "dir": "rtl",
        "prof_space": "👨‍🏫 فضاء الأستاذ",
        "student_space": "🎓 فضاء الطالب",
        "tabs": ["📝 إنشاء اختبار", "👥 الأقسام", "📊 النتائج", "📜 الأرشيف", "⚙️ الإعدادات"],
        "q_label": "السؤال المطروح",
        "q_ans": "الإجابات المتوقعة (للتنقيط التلقائي)",
        "add_q": "➕ إضافة السؤال للاختبار",
        "save_test": "💾 نشر الاختبار للطلاب",
        "res_title": "إجابات الطلاب للتصحيح",
        "hist_title": "سجل النقط",
        "note_label": "وضع علامة /20",
        "tel_label": "اختر رقم هاتفك",
        "nom_label": "أدخل اسمك الكامل",
        "start_exam": "🚀 بدء الاختبار",
        "time_rem": "الوقت المتبقي",
        "send": "إرسال إجابتي للأستاذ",
        "finish": "✅ تم إرسال إجاباتك بنجاح للأستاذ!",
        "no_test": "لا يوجد اختبار متاح حالياً.",
        "import_btn": "استيراد قائمة الطلاب",
        "class_label": "اختر قسمك",
        "reset_btn": "🗑️ إعادة ضبط الكل",
        "rep_label": "إجابتك:"
    }
}

# --- FONCTIONS DE DONNÉES ---
def load_data(file):
    if os.path.exists(file):
        try:
            with open(file, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return {}
    return {}

def save_data(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- INITIALISATION ---
st.set_page_config(page_title="EduQuiz Pro", layout="wide")
lang = st.sidebar.selectbox("Langue / اللغة", ["Français", "العربية"])
T = LANGS[lang]

# Support RTL pour l'Arabe
st.markdown(f"<style>body {{ direction: {T['dir']}; text-align: {'right' if T['dir']=='rtl' else 'left'}; }}</style>", unsafe_allow_html=True)

if 'tests' not in st.session_state: st.session_state.tests = load_data(DB_TESTS)
if 'students' not in st.session_state: st.session_state.students = load_data(DB_STUDENTS)
if 'results' not in st.session_state: st.session_state.results = load_data(DB_RESULTS)
if 'temp_qs' not in st.session_state: st.session_state.temp_qs = []

role = st.sidebar.radio("Menu", [T["prof_space"], T["student_space"]])

# ---------------------------------------------------------
# ESPACE ENSEIGNANT (PROFESSEUR)
# ---------------------------------------------------------
if role == T["prof_space"]:
    pin = st.sidebar.text_input("PIN", type="password")
    if pin == TEACHER_PIN:
        tabs = st.tabs(T["tabs"])
        
        with tabs[0]: # CRÉER TEST
            st.subheader(T["tabs"][0])
            c1, c2, c3 = st.columns(3)
            test_id = c1.text_input("Identifiant du Test (ex: Quiz1)")
            target_cl = c2.selectbox(T["class_label"], list(st.session_state.students.keys()) if st.session_state.students else ["-"])
            duration = c3.number_input("Secondes par Question", 10, 600, 60)
            
            with st.form("q_form", clear_on_submit=True):
                txt = st.text_input(T["q_label"])
                ans = st.text_area(T["q_ans"])
                cnt = st.number_input("Nombre d'éléments à citer", 1, 20, 1)
                if st.form_submit_button(T["add_q"]):
                    if txt:
                        st.session_state.temp_qs.append({
                            "text": txt, 
                            "ans": [a.strip().lower() for a in ans.split(',') if a.strip()], 
                            "count": cnt, "time": duration
                        })
                        st.success("Question ajoutée !")

            if st.session_state.temp_qs:
                if st.button(T["save_test"]):
                    st.session_state.tests[test_id] = {"classe": target_cl, "questions": st.session_state.temp_qs}
                    save_data(DB_TESTS, st.session_state.tests)
                    st.session_state.temp_qs = []
                    st.success("Test publié !")
                    st.rerun()

        with tabs[1]: # CLASSES
            st.subheader(T["tabs"][1])
            cl_name = st.text_input("Nom de la Classe")
            file = st.file_uploader("Fichier Excel/CSV (Nom, Tel)", type=['xlsx', 'csv'])
            if st.button(T["import_btn"]):
                if cl_name and file:
                    df = pd.read_excel(file) if file.name.endswith('.xlsx') else pd.read_csv(file)
                    df.columns = [c.lower() for c in df.columns]
                    col_n = next((c for c in df.columns if 'nom' in c), 'Nom')
                    col_t = next((c for c in df.columns if 'tel' in c), 'Telephone')
                    df = df.rename(columns={col_n: 'Nom', col_t: 'Telephone'})
                    df['Telephone'] = df['Telephone'].astype(str).str.replace('.0', '', regex=False)
                    st.session_state.students[cl_name] = df[['Nom', 'Telephone']].to_dict(orient='records')
                    save_data(DB_STUDENTS, st.session_state.students)
                    st.success("Importation terminée !")

        with tabs[2]: # RÉSULTATS (CORRECTION)
            st.subheader(T["res_title"])
            res = load_data(DB_RESULTS)
            for r_id, d in list(res.items()):
                with st.expander(f"📱 {d['tel']} - {d['name']} [{d['classe']}]"):
                    st.write(f"**Test:** {d['test_name']}")
                    for q_res in d['details']:
                        st.write(f"❓ **Question :** {q_res['q']}")
                        st.write(f"💬 **Réponse élève :** {q_res['provided']}")
                        st.divider()
                    note = st.number_input(T["note_label"], 0, 20, int(d.get('final_grade', 0)), key=f"note_{r_id}")
                    if st.button("Valider la note", key=f"save_{r_id}"):
                        res[r_id]['final_grade'] = note
                        save_data(DB_RESULTS, res)
                        st.rerun()

        with tabs[3]: # HISTORIQUE
            st.subheader(T["hist_title"])
            res = load_data(DB_RESULTS)
            if res:
                df_h = pd.DataFrame([{"Nom": v['name'], "Classe": v['classe'], "Test": v['test_name'], "Note/20": v.get('final_grade', 0)} for v in res.values()])
                st.table(df_h.sort_values("Note/20", ascending=False))

        with tabs[4]: # PARAMÈTRES
            st.subheader("⚙️ " + T["reset_btn"])
            if st.button(T["reset_btn"]) and st.checkbox("Confirmer"):
                for f in [DB_TESTS, DB_STUDENTS, DB_RESULTS]:
                    if os.path.exists(f): os.remove(f)
                st.session_state.clear()
                st.rerun()

# ---------------------------------------------------------
# ESPACE ÉLÈVE (MOBILE)
# ---------------------------------------------------------
else:
    st.header(T["student_space"])
    
    if not st.session_state.tests:
        st.warning(T["no_test"])
    else:
        # ÉTAPE 1 : L'ÉLÈVE S'IDENTIFIE
        if 'active_test' not in st.session_state:
            cl_sel = st.selectbox(T["class_label"], list(st.session_state.students.keys()))
            if cl_sel:
                # Liste des numéros de téléphone de la classe
                tels = [str(s['Telephone']) for s in st.session_state.students[cl_sel]]
                tel_sel = st.selectbox(T["tel_label"], tels)
                nom_sel = st.text_input(T["nom_label"])
                
                # Liste des tests créés par le prof pour cette classe
                tests_po_classe = [n for n, t in st.session_state.tests.items() if t['classe'] == cl_sel]
                test_sel = st.selectbox("Choisir l'épreuve", tests_po_classe)
                
                if st.button(T["start_exam"]) and nom_sel:
                    st.session_state.student_user = nom_sel
                    st.session_state.student_tel = tel_sel
                    st.session_state.student_classe = cl_sel
                    st.session_state.active_test = test_sel
                    st.session_state.curr_idx = 0
                    st.session_state.logs = []
                    st.session_state.q_start = time.time()
                    st.rerun()
        
        # ÉTAPE 2 : L'ÉLÈVE RÉPOND AUX QUESTIONS DU PROF
        else:
            t_info = st.session_state.tests[st.session_state.active_test]
            qs = t_info['questions']
            idx = st.session_state.curr_idx
            
            if idx < len(qs):
                q = qs[idx]
                # Chronomètre
                elapsed = time.time() - st.session_state.q_start
                rem = int(q['time'] - elapsed)
                
                if rem <= 0: # Si temps écoulé, on passe à la suite
                    st.session_state.logs.append({"q": q['text'], "provided": "TEMPS ÉCOULÉ", "is_correct": False})
                    st.session_state.curr_idx += 1
                    st.session_state.q_start = time.time()
                    st.rerun()
                
                # --- AFFICHAGE DE LA QUESTION DU PROF ---
                st.subheader(f"Question {idx+1} / {len(qs)}")
                st.info(f"👉 **{q['text']}**") # Voici la question que le prof a rédigée
                st.error(f"⏱ {T['time_rem']} : {rem}s")
                
                with st.form(key=f"q_eleve_{idx}"):
                    # L'élève saisit lui-même sa réponse
                    rep_eleve = st.text_area(T["rep_label"], placeholder="Tapez votre réponse ici...", height=150)
                    
                    if st.form_submit_button(T["send"]):
                        # Logique de calcul du score automatique (caché pour l'élève)
                        r_clean = [r.strip().lower() for r in rep_eleve.replace('\n', ',').split(',') if r.strip()]
                        matches = [r for r in r_clean if r in q['ans']]
                        is_ok = len(set(matches)) >= q['count'] if q['ans'] else False
                        
                        # On enregistre la réponse brute pour que le prof la voit
                        st.session_state.logs.append({"q": q['text'], "provided": rep_eleve, "is_correct": is_ok})
                        st.session_state.curr_idx += 1
                        st.session_state.q_start = time.time()
                        st.rerun()
                
                # Rafraichissement pour le chronomètre
                time.sleep(1)
                st.rerun()
            
            else:
                # ÉTAPE 3 : FIN DU TEST ET ENVOI AU PROFESSEUR
                score_auto = int((sum(1 for x in st.session_state.logs if x['is_correct']) / len(qs)) * 100)
                res_id = f"{st.session_state.student_tel}_{st.session_state.active_test}"
                
                # On sauvegarde tout dans le fichier de résultats
                results = load_data(DB_RESULTS)
                results[res_id] = {
                    "name": st.session_state.student_user,
                    "tel": st.session_state.student_tel,
                    "classe": st.session_state.student_classe,
                    "test_name": st.session_state.active_test,
                    "auto_score": score_auto,
                    "details": st.session_state.logs,
                    "final_grade": 0,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                save_data(DB_RESULTS, results)
                
                st.success(T["finish"])
                st.balloons()
                if st.button("Terminer"):
                    del st.session_state.active_test
                    st.rerun()