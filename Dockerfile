FROM python:3.10
RUN pip install streamlit streamlit-aggrid
RUN pip install st_pages
#RUN pip install git+https://github.com/NeveIsa/streamlit_ttyd

COPY ./odtp /odtp
WORKDIR /odtp