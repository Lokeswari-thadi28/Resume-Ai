
import re

import fitz
import streamlit as st


# ---------- Page configuration ----------
st.set_page_config(
    page_title="ResumeAI | Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------- Premium styling ----------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #f8faff, #f2f5ff, #f0fbff);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #111b40, #202c5b);
    }

    [data-testid="stSidebar"] * {
        color: #f8fafc;
    }

    h1 {
        color: #172554;
        font-weight: 800 !important;
        letter-spacing: -1px;
    }

    h2, h3 {
        color: #1e2b55;
        font-weight: 700 !important;
    }

    [data-testid="stMetric"] {
        background: rgba(255,255,255,.94);
        border: 1px solid #e2e8ff;
        padding: 18px;
        border-radius: 16px;
        box-shadow: 0 6px 24px rgba(39,55,120,.06);
    }

    [data-testid="stMetricValue"] {
        color: #635bff;
        font-weight: 800;
    }

    .stButton > button {
        background: linear-gradient(100deg, #8b5cf6, #4f46e5, #2563eb);
        color: white;
        border: none;
        border-radius: 12px;
        padding: .7rem 1.2rem;
        font-weight: 700;
        min-height: 46px;
    }

    .stButton > button:hover {
        color: white;
        border: none;
        box-shadow: 0 8px 22px rgba(99,91,255,.28);
    }

    [data-testid="stFileUploader"] {
        background: rgba(255,255,255,.8);
        border: 1px dashed #a5b4fc;
        border-radius: 16px;
        padding: 14px;
    }

    .stTextArea textarea {
        border-radius: 14px;
        border: 1px solid #dbe3ff;
        background: white;
    }

    div[data-testid="stExpander"] {
        background: rgba(255,255,255,.85);
        border: 1px solid #e2e8f0;
        border-radius: 14px;
    }

    #MainMenu, footer {
        visibility: hidden;
    }

    .hero {
        padding: 1.4rem 0 .8rem 0;
    }

    .subtitle {
        color: #64748b;
        font-size: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------- Keyword processing ----------
STOPWORDS = {
    "the", "and", "for", "with", "you", "your", "are",
    "our", "this", "that", "from", "have", "has", "will",
    "can", "all", "not", "but", "was", "were", "who",
    "what", "when", "where", "how", "their", "they",
    "them", "his", "her", "she", "him", "its", "into",
    "about", "using", "use", "used", "job", "role",
    "work", "working", "experience", "years", "year",
    "required", "requirements", "preferred", "ability",
    "skills", "skill", "strong", "good", "knowledge",
    "team", "teams", "responsibilities", "responsibility",
    "candidate", "candidates", "must", "should", "such",
    "including", "across", "other", "more", "some", "any",
    "each", "both", "also", "well", "within", "through",
    "than", "then", "they", "these", "those", "been",
    "being", "per", "etc", "etcetera", "able", "may",
    "new", "one", "two", "workplace", "environment",
}


def extract_pdf_text(pdf_file):
    """Extract selectable text from an uploaded PDF."""
    with fitz.open(
        stream=pdf_file.getvalue(),
        filetype="pdf",
    ) as document:
        return "\n".join(
            page.get_text() for page in document
        ).strip()


def get_keywords(text):
    """Extract distinct words and common technical terms."""
    words = re.findall(
        r"[a-zA-Z][a-zA-Z0-9+#.-]*",
        text.lower(),
    )

    return {
        word.strip(".-")
        for word in words
        if len(word.strip(".-")) > 1
        and word.strip(".-") not in STOPWORDS
    }


def compare_resume(resume, job):
    """Compare resume and job-description keywords."""
    job_words = get_keywords(job)
    resume_words = get_keywords(resume)

    if not job_words:
        return 0, [], []

    matched = sorted(job_words & resume_words)
    missing = sorted(job_words - resume_words)

    score = round(len(matched) / len(job_words) * 100)

    return score, matched, missing


def analyze_resume(resume, job):
    """
    Offline rule-based analysis.
    No API key, external AI service, or API billing required.
    """
    word_count = len(resume.split())
    score, matched, missing = compare_resume(resume, job)

    resume_lower = resume.lower()

    sections_to_check = {
        "Contact information": [
            "email", "phone", "linkedin",
        ],
        "Professional summary": [
            "summary", "profile", "objective",
        ],
        "Work experience": [
            "experience", "employment", "professional experience",
        ],
        "Education": [
            "education", "university", "degree",
        ],
        "Projects": [
            "projects", "project experience",
        ],
        "Technical skills": [
            "technical skills", "skills", "technologies",
        ],
        "Certifications": [
            "certifications", "certificates",
        ],
    }

    detected_sections = []
    missing_sections = []

    for section, indicators in sections_to_check.items():
        if any(indicator in resume_lower for indicator in indicators):
            detected_sections.append(section)
        else:
            missing_sections.append(section)

    report = f"""# Resume Analysis Report

## 1. Resume overview

- Approximate word count: {word_count}
- Job description provided: {"Yes" if job.strip() else "No"}
- Distinct job-description keywords matched: {len(matched)}
- Potential missing keywords: {len(missing) if job.strip() else "Not evaluated"}
- Keyword match score: {f"{score}%" if job.strip() else "Not available"}

This report is generated locally using text matching and basic
resume checks. It is not generated by a large language model.

## 2. Strengths and matched keywords

"""

    if job.strip() and matched:
        report += "\n".join(
            f"- {word}" for word in matched[:30]
        )
    elif job.strip():
        report += (
            "No matching keywords were identified. Review the "
            "job requirements and your resume wording."
        )
    else:
        report += (
            "Paste a job description to identify matching keywords. "
            "You can still use the general recommendations below."
        )

    report += "\n\n## 3. Keywords to consider highlighting\n\n"

    if job.strip() and missing:
        report += "\n".join(
            f"- {word}" for word in missing[:30]
        )
        report += (
            "\n\nOnly include a keyword if it truthfully describes "
            "your skills, experience, or qualifications."
        )
    elif job.strip():
        report += "No missing keywords were detected by this comparison."
    else:
        report += (
            "No job description was provided, so missing keywords "
            "could not be evaluated."
        )

    report += "\n\n## 4. Resume sections detected\n\n"

    report += "\n".join(
        f"- ✅ {section}" for section in detected_sections
    ) or "- No common section headings detected."

    if missing_sections:
        report += "\n\nSections to review:\n\n"
        report += "\n".join(
            f"- {section}" for section in missing_sections
        )
        report += (
            "\n\nSome sections may exist under different headings. "
            "Review your resume before adding new sections."
        )

    report += """

## 5. Practical recommendations

- Tailor your professional summary to the target position.
- Highlight relevant projects, tools, and technical skills.
- Describe accomplishments with measurable outcomes where possible.
- Start bullet points with clear action verbs.
- Keep dates, headings, and formatting consistent.
- Check spelling, grammar, email address, and phone number.
- Use a clean layout that is easy for recruiters to scan.
- Include relevant certifications when you have earned them.

## 6. Example achievement format

Use this as a template, replacing the placeholders with truthful details:

"Developed [project or solution] using [tools or technologies],
resulting in [measurable outcome or improvement]."

Do not claim results or skills you cannot verify.

## 7. Important limitations

This is a rule-based offline review, not generative AI or an official
Applicant Tracking System (ATS) score. Keyword overlap does not
measure context, proficiency, relevance, or hiring probability.

The automated section checks look for common words and may miss
sections written using different terminology. Review the report
before making changes to your resume.
"""

    return report


# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("# ✨ ResumeAI")
    st.caption("YOUR PERSONAL CAREER COPILOT")
    st.divider()

    st.markdown("🏠  Home")
    st.markdown("📄  Resume Analysis")
    st.markdown("🎯  Skills & Job Match")
    st.markdown("💡  Career Tips")

    st.divider()

    st.info(
        "Your next opportunity starts with a stronger resume."
    )

    st.caption("🔒 Local analysis mode · No API key required")


# ---------- Main page ----------
st.markdown(
    """
    <div class="hero">
        <h1>Your Resume, Smarter ✨</h1>
        <p class="subtitle">
            Discover your strengths, compare job requirements,
            and improve your resume with practical feedback.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption(
    "✦ OFFLINE RESUME REVIEW · SKILLS COMPARISON · CAREER INSIGHTS"
)

st.write("")


# ---------- Upload and job description ----------
with st.container(border=True):
    st.subheader("📄 Let's analyze your resume")

    st.write(
        "Upload a PDF and optionally paste a job description "
        "to compare your resume against the role."
    )

    left_col, right_col = st.columns(2, gap="large")

    with left_col:
        st.markdown("### 📂 Upload your resume")
        st.caption("PDF format · Maximum 5 MB")

        uploaded_file = st.file_uploader(
            "Choose your resume",
            type=["pdf"],
            key="resume_upload",
        )

    with right_col:
        st.markdown("### 🎯 Target job")
        st.caption(
            "Paste the job requirements for a more useful comparison."
        )

        job_description = st.text_area(
            "Job description",
            placeholder=(
                "Paste the job requirements here...\n\n"
                "Example: Python developer with SQL, API "
                "development, data analysis, and problem-solving skills."
            ),
            height=170,
            key="job_description_input",
        )

st.caption(
    "🔒 Resume text is processed locally by this app. "
    "This version does not send your resume to an AI provider."
)


# ---------- Resume results ----------
if uploaded_file is not None:

    if uploaded_file.size > 5 * 1024 * 1024:
        st.error("Please upload a PDF smaller than 5 MB.")
        st.stop()

    try:
        resume_text = extract_pdf_text(uploaded_file)
    except Exception:
        st.error(
            "Unable to read this PDF. Please try another PDF file."
        )
        st.stop()

    if len(resume_text) < 50:
        st.warning(
            "Very little text was extracted. This may be a scanned "
            "PDF. Try a text-based PDF; scanned documents may need OCR."
        )
        st.stop()

    with st.expander("👀 Preview extracted resume text"):
        st.text(resume_text[:5000])

    # ---------- Job match overview ----------
    if job_description.strip():
        score, matched, missing = compare_resume(
            resume_text,
            job_description,
        )

        st.divider()
        st.subheader("📊 Your job match overview")

        col1, col2, col3 = st.columns(3)

        col1.metric("🎯 Keyword overlap", f"{score}%")
        col2.metric("✅ Matched keywords", len(matched))
        col3.metric("⚡ Missing keywords", len(missing))

        st.progress(score / 100)

        matched_col, missing_col = st.columns(2, gap="large")

        with matched_col:
            with st.container(border=True):
                st.markdown("### ✅ Matched keywords")

                if matched:
                    st.write(" · ".join(matched))
                else:
                    st.write("No matching keywords found yet.")

        with missing_col:
            with st.container(border=True):
                st.markdown("### 🎯 Skills to highlight")

                if missing:
                    st.write(" · ".join(missing))
                else:
                    st.success("No missing keywords detected.")

        st.caption(
            "This is a simple unique-word comparison, not an official "
            "ATS score. It does not measure context or skill proficiency."
        )

    # ---------- Offline analysis button ----------
    st.write("")

    if st.button(
        "✨ Analyze My Resume",
        type="primary",
        use_container_width=False,
    ):
        with st.spinner("Reviewing your resume..."):
            report = analyze_resume(
                resume_text,
                job_description,
            )

            st.session_state["resume_report"] = report
            st.session_state["resume_report_name"] = uploaded_file.name

    # ---------- Report ----------
    saved_report = st.session_state.get("resume_report", "")

    if saved_report:
        st.divider()
        st.subheader("💡 Your Resume Analysis Report")

        st.markdown(saved_report)

        st.download_button(
            "⬇️ Download your resume report",
            data=saved_report,
            file_name="resume_analysis.txt",
            mime="text/plain",
        )

else:
    # Welcome state when no PDF has been uploaded.
    st.write("")

    with st.container(border=True):
        st.markdown("### 🚀 Get started")
        st.write(
            "Upload your resume PDF above to see the extracted text, "
            "compare keywords with a job description, and generate "
            "your local resume review."
        )

        st.markdown(
            "- 📊 Review keyword overlap\n"
            "- 🎯 Find potentially missing job-description keywords\n"
            "- 📝 Get practical resume improvement suggestions\n"
            "- 📥 Download your analysis report"
        )


# ---------- Footer ----------
st.divider()

st.caption(
    "✨ Keep your resume truthful. Review suggestions before using them."
)

st.caption(
    "ResumeAI Offline Edition · Private, rule-based analysis"
)
