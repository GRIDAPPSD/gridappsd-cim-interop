# Use the base application container to allow the application to be controlled
# from the gridappsd container.
FROM gridappsd/app-container-base

# Pick a spot to put our application code
# (note gridappsd-python is located at /usr/src/gridappsd-python)
WORKDIR /usr/src/gridappsd-sample

# Add dependencies to the requirements.txt file before
# uncommenting the next two lines
# COPY requirements.txt ./
# RUN RUN pip install --no-cache-dir -r requirements.txt

# Copy all of the source over to the container.
COPY . .

# Allow the sample_app/runsample.py script to be run directly from
# the command line.
RUN chmod +x sample_app/runsample.py

# Use a symbolic link to the sample app rather than having to
# mount it at run time (note can still be overriden in docker-compose file)
RUN ln -s /usr/src/gridappsd-sample/sample_app.config /appconfig