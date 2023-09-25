from barfi import st_barfi, barfi_schemas, Block
import streamlit as st

from barfi import Block

st.set_page_config(
    page_title="ODPT",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/odtp-org',
        'Report a bug': "carlos.vivarrios@epfl.ch",
        'About': "# ODTP"
    }
)

st.markdown("# Workflow Designer")

######################################################################

# MongoDB

mongodbBlock = Block(name='Mongo DB')

mongodbBlock.add_option(name='display-mongodb-address', type='display', value='Mongo DB Address')
mongodbBlock.add_option(name='mongodb-address', type='input')

mongodbBlock.add_option(name='display-mongodb-user', type='display', value='Mongo DB User')
mongodbBlock.add_option(name='mongodb-user', type='input')

mongodbBlock.add_option(name='display-mongodb-password', type='display', value='Mongo DB Password')
mongodbBlock.add_option(name='mongodb-password', type='input')

mongodbBlock.add_output(name='MongoDB')

def configmongodb(self):
    address = self.get_option(name='mongodb-address')
    user = self.get_option(name='mongodb-user')
    password = self.get_option(name='mongodb-password')

    ## To be developed

    self.set_interface(name='MongoDB', value="test")

mongodbBlock.add_compute(configmongodb)

######################################################################

# MongoDB

s3Block = Block(name='S3 Storage')

s3Block.add_option(name='display-s3-server', type='display', value='S3 Server')
s3Block.add_option(name='s3-server', type='input')

s3Block.add_option(name='display-s3-access-key', type='display', value='S3 Access Key')
s3Block.add_option(name='s3-access-key', type='input')

s3Block.add_option(name='display-s3-secret-key', type='display', value='S3 Secret Key')
s3Block.add_option(name='s3-secret-key', type='input')

s3Block.add_option(name='display-s3-bucket-name', type='display', value='S3 Bucket Name')
s3Block.add_option(name='s3-bucket-name', type='input')

s3Block.add_output(name='s3')

def configs3(self):
    server = self.get_option(name='s3-server')
    access_key = self.get_option(name='s3-access-key')
    secret_key = self.get_option(name='s3-secret-key')
    bucket_name = self.get_option(name='s3-bucket-name')

    ## To be developed

    self.set_interface(name='s3', value="test")

s3Block.add_compute(configs3)



######################################################################

#Eqasim dataloader

dataloader = Block(name='Eqasim dataloader')
dataloader.add_option(name='display-option', type='display', value='Select the eqasim pipeline.')
dataloader.add_option(name='select-option', type='select', items=['IDF', 'CH'], value='IDF')

dataloader.add_option(name='display-input', type='display', value='Introduce data folder.')
dataloader.add_option(name='file-path-input', type='input')

dataloader.add_output(name='Mounted Volume')

def eqasim_dataloader(self):
    scenario = self.get_option(name='select-option')
    link = self.get_option(name='file-path-input')

    #Download link. Would be cool if it's uploaded in the interface. 

    #Prepare folder

    folder = "pathtofolder"
    self.set_interface(name='Mounted Volume', value=folder)

dataloader.add_compute(eqasim_dataloader)

##############################################################################
# Eqasim synthetic pipeline

eqasim_synthetic = Block(name='Eqasim synthetic population')

# IDF
eqasim_synthetic.add_option(name='display-idf', type='display', value='IDF')
eqasim_synthetic.add_option(name='display-idf-processes', type='display', value='IDF processes')
eqasim_synthetic.add_option(name='idf-processes', type='integer')

eqasim_synthetic.add_option(name='display-idf-sampling-rate', type='display', value='IDF sampling rate')
eqasim_synthetic.add_option(name='idf-sampling-rate', type='slider', min=0, max=1, value=0.001)

eqasim_synthetic.add_option(name='display-idf-random-seed', type='display', value='IDF random seed')
eqasim_synthetic.add_option(name='idf-random-seed', type='integer')

eqasim_synthetic.add_option(name='display-idf-java-memory', type='display', value='IDF java memory')
eqasim_synthetic.add_option(name='idf-java-memory', type='integer')

eqasim_synthetic.add_option(name='display-idf-hts', type='display', value='IDF household')
eqasim_synthetic.add_option(name='idf-hts', type='select', items=['entd', 'egt'], value='entd')

# CH
eqasim_synthetic.add_option(name='display-ch', type='display', value='CH')
eqasim_synthetic.add_option(name='display-ch-threads', type='display', value='CH Threads')
eqasim_synthetic.add_option(name='ch-threads', type='integer', value=4)

eqasim_synthetic.add_option(name='display-ch-random-seed', type='display', value='CH random seed')
eqasim_synthetic.add_option(name='ch-random-seed', type='integer', value=0)

eqasim_synthetic.add_option(name='display-ch-hot-deck-matching-runners', type='display', value='CH hot deck matching runners')
eqasim_synthetic.add_option(name='ch-hot-deck-matching-runners', type='integer', value=2)

eqasim_synthetic.add_option(name='display-ch-java-memory', type='display', value='CH java memory')
eqasim_synthetic.add_option(name='ch-java-memory', type='integer', value=100)

eqasim_synthetic.add_option(name='display-ch-input-downscaling', type='display', value='CH input downscaling')
eqasim_synthetic.add_option(name='ch-input-downscaling', type='slider', min=0, max=1, value=0.01)

eqasim_synthetic.add_option(name='display-ch-enable-scaling', type='display', value='CH enable scaling')
eqasim_synthetic.add_option(name='ch-enable-scaling', type='checkbox')

eqasim_synthetic.add_option(name='display-ch-scaling-year', type='display', value='CH scaling year')
eqasim_synthetic.add_option(name='ch-scaling-year', type='integer', value=2020)

eqasim_synthetic.add_option(name='display-ch-use-freight', type='display', value='CH use freight')
eqasim_synthetic.add_option(name='ch-use-freight', type='checkbox')

eqasim_synthetic.add_option(name='display-ch-hafas-date', type='display', value='CH hafas date')
eqasim_synthetic.add_option(name='ch-hafas-date', type='input', value="01.10.2018")

eqasim_synthetic.add_option(name='display-ch-output-id', type='display', value='CH output-id')
eqasim_synthetic.add_option(name='ch-output-id', type='input', value="test")

eqasim_synthetic.add_input(name="scenario")
eqasim_synthetic.add_input(name="volume")
eqasim_synthetic.add_input(name="mongodb")
eqasim_synthetic.add_input(name="s3")

eqasim_synthetic.add_output(name="output")

def runEqasimSynthetic(self):
    scenario = self.get_interface(name='scenario')
    # TO BE DEVELOPED

    self.set_interface(name="output", value="v")


eqasim_synthetic.add_compute(runEqasimSynthetic)


##############################################################################
# Eqasim matsim preparation

eqasim_matsim = Block(name='Eqasim matsim preparation')

eqasim_matsim.add_option(name='display-eqasim-matsim', type='display', value='TODO: Add relevant parameters here.')

eqasim_matsim.add_input(name="eqasim synthetic")
eqasim_matsim.add_input(name="volume")
eqasim_matsim.add_input(name="mongodb")
eqasim_matsim.add_input(name="s3")

eqasim_matsim.add_output(name="output")

def runEqasimMatsim(self):
    synthetic = self.get_interface(name="eqasim synthethic")

    # TO BE DONE

    self.set_interface(name="output", value="test")

eqasim_matsim.add_compute(runEqasimMatsim)

##############################################################################
# Matsim

matsim = Block(name='Matsim')
matsim.add_option(name='display-matsim', type='display', value='TODO: Add relevant parameters here.')


matsim.add_input(name="eqasim matsim")
matsim.add_input(name="volume")
matsim.add_input(name="mongodb")
matsim.add_input(name="s3")

matsim.add_output(name="output")

def runMatsim(self):
    synthetic = self.get_interface(name="eqasim matsim")

    # TO BE DONE

    self.set_interface(name="output", value="test")

matsim.add_compute(runMatsim)

##############################################################################

splitter = Block(name='Splitter')
splitter.add_input()
splitter.add_output()
splitter.add_output()
def splitter_func(self):
    in_1 = self.get_interface(name='Input 1')
    value = (in_1/2)
    self.set_interface(name='Output 1', value=value)
    self.set_interface(name='Output 2', value=value)
splitter.add_compute(splitter_func)

mixer = Block(name='Mixer')
mixer.add_input()
mixer.add_input()
mixer.add_output()
def mixer_func(self):
    in_1 = self.get_interface(name='Input 1')
    in_2 = self.get_interface(name='Input 2')
    value = (in_1 + in_2)
    self.set_interface(name='Output 1', value=value)
mixer.add_compute(mixer_func)

result = Block(name='Result')
result.add_input()
def result_func(self):
    in_1 = self.get_interface(name='Input 1')
result.add_compute(result_func)

load_schema = st.selectbox('Select a saved schema:', barfi_schemas())

compute_engine = st.checkbox('Activate barfi compute engine', value=False)

barfi_result = st_barfi(base_blocks=[mongodbBlock, s3Block, dataloader,
                                     eqasim_synthetic, eqasim_matsim, matsim,
                                     result, mixer, splitter],
                    compute_engine=compute_engine, load_schema=load_schema)

if barfi_result:
    st.write(barfi_result)