# NeighborNet WebApp

WebApp for grouping people living at identical addresses, by parsing `.csv` files or raw comma separated text.

## Installation

1. Clone the repo:

`git clone https://github.com/Mishakaveli1994/ResonanzWebApp.git`

2. Use the `setup.py` file to install NeighborNet application:

```
python setup.py install
```

3. Specify the project's name in the terminal variables:

* Bash - `export FLASK_APP=neighbor_net`
* cmd - `set FLASK_APP=neighbor_net`
* Powershell - `$env:FLASK_APP = "neighbor_net"`

4. Go into the newly downloaded project: `cd ResonanzWebApp`


5. Run the web app with: `flask run`

## Usage

* Either manually input a comma delimited text in the `CSV Manual input` text area, or upload a file with the provided
  file picking button.


* Select your DataFrame processing framework - `Polars`, `Pandas` or `Dask`. I have specifically made 3 implementations
  in the course of the project to see which one would perform best.


* When you have provided an input to process and have selected the desired DataFrame processor, click the
  `Group By Addess button` This will trigger an AJAX POST request that will send the data, wait for it to be processed
  and display the result in the `Output` text area.


* After the data is displayed, 2 more outputs will be shown - the total time for processing and a `Download` button -
  with it
  you can download the resulted data.

## Internal Implementation

1. HTML pre-checks

* Before the data is sent to the backend, a few tests are performed on the input:
    * Is there any provided input in either the textarea or via the input file button
        * If both are empty, an alert is raised to provide proper input data
    * Is there data provided in both fields
        * This will raise alert, requesting that only 1 input option is filled
    * Is the provided file larger than 10 MB
        * If it is, an alert will be raised to ask for a smaller file. This is more due to security reasons, than
          inability of the pipeline to process the data
    * Is a folder selected instead of a file
        * In some platforms (like Linux), you can select a folder in some instances, instead of a file
          If this is located, ask for a file to be provided

2. The pipeline of all processing libraries (`Polars`, `Pandas`, `Dask`) is largely the same, achieved via UDF functions

* Read the data as a Stream - if file `IO[bytes]`, if plain text - `io.StringIO`. When streaming, no need to worry about
  file management, and also if needed, if the input file size was extended to be more than the ram, most frameworks can
  perform their actions in a streaming manner, not impacting the hardware resources as much.


* `Pandas` and `Dask` processing (`Dask` initially uses a `Pandas` dataframe, due to its inability to read from streams
  itself)
  perform general checks on the data.


* If an address is found to contains symbols outside the ascii range, google translation service is used to convert
  it to ascii - implemented `lru_cache` in case same token in found multiple times, speeds the pipeline enormously in
  those cases


* The addresses are converted to lower case as this provides optimizations for the next step


* Perform `fuzzy-matching` - an actions that uses the `Levenshtein Distance` measuring algorithm, to calculate the
  similarity between strings. In this specific example `Token Set Ratio` method is used as it excels in comparing
  strings
  with significant overlaps, but also may include more words


* Group the names by the match output of the `fuzzy-matching` operation - this will provide an unordered list of lists
  that is momentarily also converted to a set, to remove duplicates if any


* First sort each internal list and the outer list by the values of the inner ones


* Return the output to HTML page

### Unimplemented ideas

* Asynchronous translation - I think if needed, async can be effectively be used to send data to the google translation
  service.
* Local translation model - this will probably perform better, as no bandwidth will be used, but for the sake of keeping
  the project simple, it will not be implemented.