[rewrite_local]

https://api.m.jd.com/client.action(.+)newUserInfo url script-response-body https://raw.githubusercontent.com/jichun29/tools/main/QuantumultX/JD/JDwskey.js

[mitm]

hostname = api.m.jd.com
