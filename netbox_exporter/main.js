#!/usr/bin/env node
"use strict"

var async = require('./async');
var exec = require('child_process').exec;
var fs = require('fs');
var http = require('http');
var https = require('https');
var url = require('url');

function fetch_report(cb) {
	var cmds = ["sysinfo", "vmadm lookup -j", "imgadm list -j"];
	async.map(cmds,
		function(cmd, cb) {
			exec(cmd, {maxBuffer: 32*1024*1024}, function(err, stdout, stderr) {
				if (err) return cb(err);
				cb(null, JSON.parse(stdout));
			})
		},
		function(err, results) {
			if (err) return cb(err);
			cb(null, {
				"sysinfo": results[0],
				"vm": results[1],
				"img": results[2],
			})
		}
	)
}

function post_data(url_, data) {
	var post_data = JSON.stringify(data);
	var options = url.parse(url_);
	var http_module = null
	if (options["protocol"] == "http:") {
		http_module = http;
	} else if (options["protocol"] == "https:") {
		http_module = https;
	} else {
		throw new Error("Invalid URL scheme.");
	}
	options["method"] = "POST";
	options["headers"] = {
		'Content-Type': 'application/json',
		'Content-Length': Buffer.byteLength(post_data)
	}
	var req = http_module.request(options, function(res) {
		if (res.statusCode != 200) {
			console.log("status: ", res.statusCode);
		}
		res.on('data', function(d) {
			if (res.statusCode != 200) {
				process.stdout.write(d);
			}
		});
	});

	req.on('error', function(e) {
		console.log('problem with request: ' + e.message);
	});

	req.write(post_data);
	req.end();
}

function post_report() {
	fetch_report(function(err, report) {
		if (err) {
			console.log(err);
			return;
		}
		post_data(config.url + "/api/plugins/smartos/report",
			{
				"report": report,
				"token": config.token,
			}
		);
	})
}


var config_path = process.env.NETBOX_EXPORTER_CONFIG || "/opt/netbox_exporter/config.json"
var config = JSON.parse(fs.readFileSync(config_path, 'utf8'));

if (!("url" in config)) {
	console.log("Need to set 'url' in config.")
	return
}

if (!("token" in config)) {
	console.log("Need to set 'token' in config.")
	return
}

if (process.argv.indexOf("-d") >= 0) {
	setInterval(post_report, (config.interval || (6 * 60 * 60)) * 1000)
}

post_report()
