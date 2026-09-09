\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{ut-proposal}[2026/08/17 University of Tehran proposal form]

\LoadClass[11pt,letterpaper]{article}

\RequirePackage[letterpaper,top=0.90in,bottom=0.68in,left=0.75in,right=0.75in]{geometry}
\RequirePackage{xcolor}
\RequirePackage{graphicx}
\RequirePackage{tikz}
\RequirePackage{eso-pic}
\RequirePackage{tabularx}
\RequirePackage{array}
\RequirePackage{multirow}
\RequirePackage{makecell}
\RequirePackage{amssymb}
\RequirePackage{enumitem}
\RequirePackage{ragged2e}
\RequirePackage[most]{tcolorbox}
\RequirePackage{fontspec}
\RequirePackage{xepersian}

\definecolor{UTBlue}{RGB}{0,112,192}
\definecolor{UTCoverBlue}{RGB}{68,114,196}
\definecolor{UTPale}{RGB}{229,243,247}
\definecolor{UTPlaceholder}{RGB}{105,105,105}

\settextfont[
  Path=assets/fonts/,
  UprightFont=Vazirmatn-Regular.ttf,
  BoldFont=Vazirmatn-Bold.ttf,
  Scale=1.02
]{Vazirmatn}
\IfFontExistsTF{Times New Roman}{
  \setlatintextfont{Times New Roman}
}{
  \setlatintextfont{TeX Gyre Termes}
}

\pagestyle{empty}
\setlength{\parindent}{0pt}
\setlength{\parskip}{2.5pt}
\linespread{1.08}
\setlist{nosep,leftmargin=*,labelsep=.45em}
\renewcommand{\arraystretch}{1.38}

\newcommand{\UTAssetPath}{assets/}
\newcommand{\UTTechnicalLogo}{\UTAssetPath technical-campus-logo.png}
\newcommand{\UTUniversityLogo}{\UTAssetPath university-of-tehran-logo.png}

\newcolumntype{Y}{>{\centering\arraybackslash}X}
\newcolumntype{R}[1]{>{\raggedleft\arraybackslash}p{#1}}
\newcolumntype{C}[1]{>{\centering\arraybackslash}p{#1}}
\newcolumntype{L}[1]{>{\raggedright\arraybackslash}p{#1}}

\newcommand{\UTCell}[1]{\strut #1\strut}
\newcommand{\UTPlaceholder}[1]{\textcolor{UTPlaceholder}{#1}}
\newcommand{\UTEmpty}{\UTPlaceholder{برای تکمیل کلیک کنید}}
\newcommand{\UTBox}{\raisebox{.1ex}{\ensuremath{\square}}}
\newcommand{\UTCheckedBox}{\raisebox{.1ex}{\ensuremath{\boxtimes}}}

\newcommand{\UTReferenceRow}{%
  \noindent\begin{tikzpicture}
    \path[use as bounding box] (0,0) rectangle (\textwidth,24pt);
    \node[anchor=east,font=\bfseries,xshift=-1.10in] at (\textwidth,12pt) {شماره مرجع:};
    \draw[gray!65,line width=.55pt] (22pt,0) rectangle +(65pt,24pt);
    \draw[gray!65,line width=.55pt] (108pt,0) rectangle +(30pt,24pt);
    \draw[gray!65,line width=.55pt] (158pt,0) rectangle +(35pt,24pt);
    \draw[gray!65,line width=.55pt] (240pt,0) rectangle +(71pt,24pt);
    \node[font=\scriptsize] at (54.5pt,12pt) {\ProposalReferencePartA};
    \node[font=\scriptsize] at (123pt,12pt) {\ProposalReferencePartB};
    \node[font=\scriptsize] at (175.5pt,12pt) {\ProposalReferencePartC};
    \node[font=\scriptsize] at (275.5pt,12pt) {\ProposalReferencePartD};
  \end{tikzpicture}%
}

\newtcolorbox{utformbox}[1][]{
  enhanced,
  colback=white,
  colframe=UTBlue,
  boxrule=.85pt,
  arc=0pt,
  outer arc=0pt,
  left=5pt,right=5pt,top=5pt,bottom=5pt,
  before skip=4pt,after skip=7pt,
  #1
}

\newtcolorbox{utproposalbox}[2][]{
  enhanced,
  breakable,
  colback=white,
  colframe=UTBlue,
  coltitle=black,
  fonttitle=\bfseries,
  title={#2},
  attach boxed title to top center={yshift=-1.5mm},
  boxed title style={colback=white,colframe=white,boxrule=0pt},
  boxrule=.8pt,
  arc=0pt,
  outer arc=0pt,
  left=8pt,right=8pt,top=12pt,bottom=7pt,
  before skip=3pt,after skip=6pt,
  pad at break*=4pt,
  #1
}

\newcommand{\UTSectionHeading}[1]{%
  \begin{center}\bfseries\large #1\end{center}\vspace{-5pt}%
}

\newcommand{\UTCoverPage}[1]{%
  \thispagestyle{empty}
  \AddToShipoutPictureBG*{%
    \begin{tikzpicture}[remember picture,overlay]
      \draw[UTCoverBlue,line width=1.45pt,rounded corners=27pt]
        ([xshift=.78in,yshift=-.90in]current page.north west)
        rectangle
        ([xshift=-.78in,yshift=.90in]current page.south east);
      \node[anchor=north west] at ([xshift=.94in,yshift=-1.02in]current page.north west)
        {\includegraphics[width=.92in]{\UTTechnicalLogo}};
      \node[anchor=north east] at ([xshift=-.94in,yshift=-1.01in]current page.north east)
        {\includegraphics[width=.79in]{\UTUniversityLogo}};
    \end{tikzpicture}%
  }%
  \noindent\begin{minipage}[t][\dimexpr\textheight-38pt\relax][t]{\textwidth}
    \centering
    \vspace{1pt}
    {\bfseries به نام خدا\par}
    \vspace{13mm}
    {\bfseries دانشکده مهندسی برق و کامپیوتر\par}
    \vspace{3mm}
    {\bfseries پردیس دانشکده‌های فنی\par}
    \vspace{3mm}
    {\bfseries دانشگاه تهران\par}
    \vspace{10mm}
    {\bfseries\Large پیشنهاد و فرم حمایت از پایان‌نامه تحصیلات تکمیلی\par}
    \vspace{5mm}
    \begin{tabular}{@{}C{.27\textwidth}C{.27\textwidth}@{}}
      \UTCell{\UTBox\quad دکتری} & \UTCell{\UTCheckedBox\quad کارشناسی ارشد}\\[3pt]
      \UTCell{\UTBox\quad نوبت دوم} & \UTCell{\UTCheckedBox\quad روزانه}
    \end{tabular}
    \vspace{11mm}
    \begin{LTR}
      \makebox[\textwidth][r]{%
        \begin{RTL}
          \begin{minipage}{.69\textwidth}
            \raggedright
            \bfseries
            نام و نام خانوادگی: مرتضی ملکی‌نژاد شوشتری\par
            شماره دانشجویی: ۸۱۰۱۰۴۲۵۶\par
            استاد راهنمای اول: دکتر محمدرضا ابوالقاسمی دهاقانی\par
            تاریخ تصویب: \ProposalApprovalDate\par
            امضا مدیر گروه: \ProposalDepartmentSignature\par
            \vspace{6mm}
            ورود به تحصیلات تکمیلی پردیس: \ProposalEntryDate\par
          \end{minipage}%
        \end{RTL}%
        \hspace{1.10in}%
      }
    \end{LTR}
    \vspace{4mm}
    \UTReferenceRow
    \vfill
    \begin{minipage}{.92\textwidth}
      \scriptsize
      \begin{enumerate}[label=\arabic*.]
        \item شماره‌ی مرجع، توسط معاونت پژوهشی پردیس دانشکده‌های فنی، هنگام صدور ابلاغ درج خواهد شد.
        \item تکمیل کلیه قسمت‌های فرم به‌صورت تایپ‌شده ضروری است و در صورت ناقص بودن هر یک از موارد، پروپوزال عودت داده خواهد شد.
      \end{enumerate}
    \end{minipage}
    \vspace{1mm}
  \end{minipage}
  \clearpage
  #1
}

\newcommand{\UTSummaryPage}{%
  \UTSectionHeading{۱- خلاصه‌ی اطلاعات پایان‌نامه}
  \begin{utformbox}[boxsep=0pt,left=0pt,right=0pt,top=0pt,bottom=0pt]
    \begin{tabularx}{\linewidth}{|C{.22\linewidth}|X|}
      \hline
      \bfseries عنوان (فارسی) & \UTCell{\ProposalTitleFa}\\ \hline
      \bfseries عنوان (انگلیسی) & \UTCell{\lr{\ProposalTitleEn}}\\ \hline
      \multicolumn{2}{|c|}{%
        \begin{tabular}{C{.13\linewidth}C{.23\linewidth}C{.23\linewidth}C{.23\linewidth}}
          \bfseries نوع & \ProposalTypeFundamental\quad بنیادی &
          \ProposalTypeApplied\quad کاربردی &
          \ProposalTypeDevelopmental\quad توسعه‌ای
        \end{tabular}}\\ \hline
    \end{tabularx}
  \end{utformbox}

  \vspace{4mm}
  \UTSectionHeading{۲- اطلاعات استاد راهنما و مشاور}
  \begin{utformbox}[boxsep=0pt,left=0pt,right=0pt,top=0pt,bottom=0pt]
    \begin{tabularx}{\linewidth}{|C{.20\linewidth}|Y|Y|Y|Y|Y|}
      \hline
      \bfseries نوع مسئولیت & \bfseries نام و نام خانوادگی & \bfseries مرتبه‌ی علمی & \bfseries درصد مشارکت & \bfseries محل خدمت & \bfseries امضا و تاریخ\\ \hline
      \makecell{
      	استاد راهنمای اول\\(مجری)} &
      	 \ProposalSupervisor & \ProposalSupervisorRank & \ProposalSupervisorShare & \ProposalSupervisorAffiliation & \ProposalSupervisorSignature\\ \hline
      \makecell{استاد راهنمای دوم\\(حسب نیاز)} & \UTEmpty & \UTEmpty & & & \rule{0pt}{10mm}\\ \hline
      استاد مشاور اول & \UTEmpty & \UTEmpty & & & \rule{0pt}{10mm}\\ \hline
      \makecell{استاد مشاور دوم\\(حسب نیاز)} & \UTEmpty & \UTEmpty & & & \rule{0pt}{10mm}\\ \hline
    \end{tabularx}
  \end{utformbox}

  \vspace{4mm}
  \UTSectionHeading{۳- اطلاعات دانشجو}
  \begin{utformbox}[boxsep=0pt,left=0pt,right=0pt,top=0pt,bottom=0pt]
    \begin{tabularx}{\linewidth}{|C{.20\linewidth}|X|C{.18\linewidth}|X|}
      \hline
      \bfseries نام و نام خانوادگی & \ProposalStudentName & \bfseries تلفن ثابت/همراه & \ProposalPhone\\ \hline
      \bfseries مقطع و نوع پذیرش & \ProposalDegreeAndAdmission & \bfseries آدرس ایمیل & \ProposalEmail\\ \hline
      \bfseries رشته و گرایش & \ProposalMajor & \bfseries امضا و تاریخ & \ProposalStudentSignature\\ \hline
    \end{tabularx}
  \end{utformbox}
  \clearpage
}

\newenvironment{UTProposalSection}[1]{%
  \begin{utproposalbox}{#1}\small\setlength{\parskip}{5pt}\justifying
}{%
  \end{utproposalbox}
}

\newcommand{\UTApprovalBox}[2]{%
  \begin{utformbox}[height=3.55in,valign=top,boxsep=0pt,left=5mm,right=5mm,top=17mm,bottom=5mm,overlay={
      \draw[black,line width=.4pt]
        ([yshift=-14mm]frame.north west) -- ([yshift=-14mm]frame.north east);
      \draw[black,line width=.4pt]
        ([xshift=30mm]frame.north west) -- ([xshift=30mm,yshift=-14mm]frame.north west);
      \draw[black,line width=.4pt]
        ([yshift=-7mm]frame.north west) -- ([xshift=30mm,yshift=-7mm]frame.north west);
      \node[anchor=center] at ([xshift=15mm,yshift=-3.5mm]frame.north west) {شماره:};
      \node[anchor=center] at ([xshift=15mm,yshift=-10.5mm]frame.north west) {تاریخ:};
      \node[anchor=east,align=right,font=\bfseries,inner sep=0pt,
        text width=\dimexpr\textwidth-40mm\relax]
        at ([xshift=-5mm,yshift=-7mm]frame.north east) {\rl{#1}};
    }]
    \textbf{با نام و یاد خدا}\par
    \vspace{2mm}
    #2\par
    \vfill
    \begin{center}
      \bfseries معاون آموزشی و تحصیلات تکمیلی پردیس دانشکده‌های فنی\par
      امضا\par
      تاریخ
    \end{center}
    \vspace{4mm}
  \end{utformbox}
}

\newcommand{\UTApprovalPage}{%
  \UTApprovalBox{معاون محترم آموزشی و تحصیلات تکمیلی پردیس دانشکده‌های فنی}{%
    فرم پیشنهاد و حمایت از پایان‌نامه جناب آقای / سرکار خانم \ProposalStudentName، دانشجوی مقطع \ProposalDegreeAndAdmission،
    جهت اطلاع و صدور ابلاغ خدمت شما ارسال می‌شود.}
  \vspace{6mm}
  \UTApprovalBox{معاون محترم پژوهشی پردیس دانشکده‌های فنی}{%
    به پیوست فرم پیشنهاد و حمایت از پایان‌نامه تحصیلات تکمیلی دانشجوی فوق که به تصویب شورای پژوهشی گروه رسیده است،
    جهت صدور ابلاغ و ادامه مراحل ارسال می‌شود.}
}

\endinput
