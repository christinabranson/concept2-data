/**
 * Script to
 */

var d = new Date();
var logDateString = d.getFullYear() + "-" + d.getMonth() + "-" + d.getDate() + "-" + d.getHours() + "-" + d.getMinutes() + "-" + d.getSeconds();

var system = require('system');
var args = system.args;

if (args.length === 1) {
    console.log('Try to pass some arguments when invoking this script!');
    phantom.exit();
}

var userArg = args[1];
var userArgValue = userArg.split("=")[1];

/**
 * Read the filesystem to get a list of json usernames and password in the format:
 *
{
  "users":[
    {
      "username":"username1",
      "password":"password1"
    },
    {
      "username":"username2",
      "password":"password2"
    }
  ]
}

 * We will then parse the javascript to get the appropriate username and password based on the argument sent in
 */
var fs = require('fs');
var env_data = fs.read('.env');
//console.log('read env_data:', env_data);
var env_obj = JSON.parse(env_data);
var LOGBOOK_USERNAME = env_obj.users[parseInt(userArgValue) - 1]["username"];
phantom.username = LOGBOOK_USERNAME;
var LOGBOOK_PASSWORD = env_obj.users[parseInt(userArgValue) - 1]["password"];
phantom.password = LOGBOOK_PASSWORD;
//console.log('credentials username:', LOGBOOK_USERNAME);
//console.log('credentials password:', LOGBOOK_PASSWORD);


var LOGBOOK_URL = "https://log.concept2.com/login";

var page = new WebPage();

//spoof it as opera mini, to get the mobile page working properly
page.settings.userAgent = "Opera/9.80 (J2ME/MIDP; Opera Mini/6.5.26955/27.1407; U; en) Presto/2.8.119 Version/11.10";

function doLogin(){
    console.log("doLogin");
    page.render('screenshots/'+logDateString+'_doLogin.png');
    page.evaluate(function(LOGBOOK_USERNAME, LOGBOOK_PASSWORD){
        console.log("so are we in this function?!");
        var forms = document.getElementsByTagName("form");
        var form = forms[0];

        form.elements["username"].value = LOGBOOK_USERNAME;
        form.elements["password"].value = LOGBOOK_PASSWORD;

        form.submit();
    }, LOGBOOK_USERNAME, LOGBOOK_PASSWORD);
}

function just_wait() {
    setTimeout(function() {
        page.render('screenshots/'+logDateString+'_just_wait.png');
        phantom.exit();
    }, 50000);
}

page.onLoadFinished = function(status){
    page.render('screenshots/'+logDateString+'_onLoadFinished.png');
    console.log("phantom state: " + (!phantom.state ? "no-state" : phantom.state));
    if(status !== "success"){
        console.log( (!phantom.state ? "no-state" : phantom.state) + ": " + status );
        phantom.exit();
    }

    if( !phantom.state ){
        doLogin();
        phantom.state = "logged-in";
    } else if (phantom.state == "logged-in") {
        console.log("now try to scrape page");
        page.render('screenshots/'+logDateString+'_postLogin.png');

        var html = page.evaluate(function(){
            return document.getElementsByTagName('body')[0].innerHTML;
        });

        // first write to file
        var fs = require('fs');
        var path = 'html/'+logDateString+'_full_page_content.txt';
        fs.write(path, html, 'w');

        page.evaluate(function(userArgValue){
            console.log("in scrape evaluate function");
            var log_table_html = document.getElementById('log-table');

            if (!log_table_html) {
                console.log("Nothing with `log-table`");
            }

            // First get an array of table headers
            var headers = [];
            var log_table_html_header_rows = log_table_html.getElementsByTagName('tr');

            for (var headerRowIterator = 0; headerRowIterator < log_table_html_header_rows.length; headerRowIterator++) {
                var header_row = log_table_html_header_rows[headerRowIterator];
                var log_table_html_header_row_columns = header_row.getElementsByTagName('th');
                for (var headerColumnIterator = 0; headerColumnIterator < log_table_html_header_row_columns.length; headerColumnIterator++) {
                    var headerColumn = log_table_html_header_row_columns[headerColumnIterator];
                    //console.log(headerColumn.innerHTML.trim());
                    headers.push(headerColumn.innerHTML.trim());
                }
            }

            console.log(headers);


            var data = [];
            var log_table_html_rows = log_table_html.getElementsByTagName('tr');

            for (var rowIterator = 0; rowIterator < log_table_html_rows.length; rowIterator++) {
                var row = log_table_html_rows[rowIterator];
                var log_table_html_row_columns = row.getElementsByTagName('td');
                if (log_table_html_row_columns.length > 0) {
                    var dataRow = new Object();
                    for (var columnIterator = 0; columnIterator < log_table_html_row_columns.length; columnIterator++) {
                        var column = log_table_html_row_columns[columnIterator];
                        if (typeof headers[columnIterator] !== 'undefined' && headers[columnIterator] != "Action") {
                            dataRow[headers[columnIterator]] = column.innerHTML.trim();
                        }
                    }
                    dataRow["User"] = userArgValue;
                    data.push(dataRow);
                }
            }
            var json = JSON.stringify(data);

            console.log(json);

            var xmlhttp = new XMLHttpRequest();   // new HttpRequest instance
            xmlhttp.open("POST", "https://concept2-data.aycdev.com/scrape/api.php");
            xmlhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
            xmlhttp.send(json);

        }, userArgValue);

        console.log("fin");
        phantom.exit();
    }
};

page.onConsoleMessage = function (message){
    console.log("msg: " + message);
};


// Start it all
page.open(LOGBOOK_URL);
