from datetime import datetime, timedelta
import requests
import os
import json

# Isi variabel dibawah dengan username dan password akun klikbca
user = ""
pin = ""


class BCA(object):
    def __init__(self, userid, pwd, date):
        self.__userid = userid
        self.__pwd = pwd
        self.__date = date
        try:
            open("cookies_"+userid+".txt")
            self.__cookie = open("cookies_"+userid+".txt").read()
        except IOError:
            self.__cookie = ""

    def __timeCustom(self, cmd):
        jarak = cmd.split("day")[0]
        t = datetime.now()
        ts = t - timedelta(days=int(jarak))
        d = t.strftime("%d")
        m = t.strftime("%m")
        y = t.strftime("%Y")
        ds = ts.strftime("%d")
        ms = ts.strftime("%m")
        ys = ts.strftime("%Y")
        dari = {"d": ds, "m": ms, "y": ys}
        ke = {"d": d, "m": m, "y": y}
        return {"dari": dari, "ke": ke}

    def __timeNow(self, t):
        d = t.strftime("%d")
        m = t.strftime("%m")
        y = t.strftime("%Y")
        dari = {"d": d, "m": m, "y": y}
        return {"dari": dari, "ke": dari}

    def __getStr(self, start, end, data):
        a = data.split(start)[1]
        b = a.split(end)[0]
        return b

    def __replaceAll(self, text, dic):
        for i, j in dic.items():
            text = text.replace(i, j)
        return text

    def __mutasiSaldo(self, name):
        data = self.__getData()["data"].replace('align="center">:</td>', "")
        find = self.__getStr('align="left">'+name+'</td>', '</td>', data)
        find = find.split('align="left">')[1]
        return find

    def __getIp(self):
        r = requests.get("https://api.ipify.org/?format=json")
        res = r.json()["ip"]
        return res

    def __login(self):
        api = "https://m.klikbca.com/authentication.do"
        body = "value(user_id)=" + self.__userid+"&value(pswd)=" + self.__pwd + \
            "&value(Submit)=LOGIN&value(actions)=login&value(user_ip)=" + self.__getIp() + \
            "&user_ip=" + self.__getIp() + "&value(mobile)=true&value(browser_info)=Mozilla/5.0 (Linux; Android 5.1.1; SM-G935FD) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.101 Safari/537.36&mobile=true"
        r = requests.post(api, data=body, headers={
            "Origin": "https://m.klikbca.com",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (Linux; Android 5.1.1; SM-G935FD) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.101 Safari/537.36",
            "Referer": "https://m.klikbca.com/login.jsp",
        })
        result = r.text
        cook = []
        for cookie in list(r.cookies):
            cook.append(cookie.value)
        if "var err='" in r.text:
            return {"status": "gagal", "msg": self.__getStr("var err='", "'", result)}
        else:
            cookie = "Cookie-NS-Mklikbca=" + \
                cook[0]+"; "+"JSESSIONID="+cook[1]+";"
            f = open("cookies_" + self.__userid+".txt", 'w')
            f.write(cookie)
            f.close()
            self.__cookie = cookie
            return {"status": "sukses", "cookies": cookie}

    def __getData(self):
        status = False
        while status == False:
            if self.__date == "today":
                t = self.__timeNow(datetime.now())
                tdari = t["dari"]
                tke = t["ke"]
            else:
                t = self.__timeCustom(self.__date)
                tdari = t["dari"]
                tke = t["ke"]
            if os.path.isfile("cookies_" + self.__userid+".txt") == False:
                login = self.__login()
                if login["status"] == "gagal":
                    return {"status": False, "data": {}, "message": login["msg"]}

            api = "https://m.klikbca.com/accountstmt.do?value(actions)=acctstmtview"
            body = "value(r1)=1&value(D1)=0&value(startDt)=" + \
                tdari["d"]+"&value(startMt)="+tdari["m"]+"&value(startYr)="+tdari["y"] + \
                "&value(endDt)=" + \
                tke["d"]+"&value(endMt)="+tke["m"] + \
                "&value(endYr)="+tke["y"]
            r = requests.post(api, data=body, headers={
                "Origin": "https://m.klikbca.com",
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "Mozilla/5.0 (Linux; Android 5.1.1; SM-G935FD) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.101 Safari/537.36",
                "Referer": "https://m.klikbca.com/accountstmt.do?value(actions)=acct_stmt",
                "Cookie": self.__cookie
            })
            result = r.text
            if "302 Moved Temporarily" in result:
                os.unlink("cookies_" + self.__userid+".txt")
            elif "TRANSAKSI GAGAL" in result:
                status = True
                return {"status": False, "data": {}, "message": "Transaksi Gagal"}
            elif "TIDAK ADA TRANSAKSI" in result:
                status = True
                return {"status": False, "data": {}, "message": "Tidak Ada Transaksi Pada Tanggal "+tdari["d"]+"/"+tdari["m"]+"/"+tdari["y"]}
            else:
                status = True
                return {"status": True, "data": result}

    def mutasiTrx(self, date=None):
        d = datetime.now().strftime("%d")
        m = datetime.now().strftime("%m")
        arr = {"  ": "", "<tr bgcolor='#e0e0e0'><td valign='top'>": "", "<tr bgcolor='#f0f0f0'><td valign='top'>": "",
               "	": "", "</tr>": "", "\r": "", "\n\n": "", "</td><td>SWITCHING DB      <br>": "", "</td><td>SWITCHING CR      <br>": ""}
        arr2 = {"<td valign='top'>": "|", "<br>": "|", "\n": "|"}
        res = self.__getData()
        try:
            stz = self.__getStr("<br>"+m+"/"+d+" ", " ", res)
        except:
            stz = ""
        arr3 = {"PEND </td><td>": "", "<br>"+m+"/"+d+" "+stz: "", "  ": ""}
        if res["status"] == True:
            res = self.__getStr(
                '<td bgcolor="#e0e0e0" colspan="2"><b>KETERANGAN</td>', '<!--<tr>', res["data"])
            res = self.__replaceAll(res, arr)
            res = self.__replaceAll(res, arr3)
            c = res.split("\n")
            arz = ["SALDO AWAL", "SALDO AKHIR",
                   "MUTASI KREDIT", "MUTASI DEBET"]
            results = {}
            results["status"] = True
            result = {}
            for i in range(len(arz)):
                name = arz[i]
                name_arr = (name.lower()).replace(" ", "_")
                results[name_arr] = self.__mutasiSaldo(name)
            for j in range(len(c)):
                res = self.__replaceAll(c[j], arr2)
                ress = (res.replace("</td>", "")).split("|")
                res1 = {}
                res1['desc1'] = ress[0]
                res1['desc2'] = ress[1]
                res1['vendor'] = ress[2]
                res1['amount'] = ress[len(ress) - 2]
                res1['type'] = ress[len(ress) - 1]
                result["Transaction #"+str(j+1)] = res1
            results["data"] = result
            return json.dumps(results, indent=4)
        else:
            return json.dumps(res, indent=4)


print(" Cek Mutasi BCA ".center(30, "="))
print(" Created By : @gidhan ".center(30, "="))
print("\nNote: ")
print("[+] Isi today (Apabila ingin cek mutasi hari ini)")
print("[+] Isi 3day (Apabila ingin cek mutasi 3 hari terakhir")
print("[+] Nb: Bisa custom hari sesuai keinginan kalian, max 30day!\n")
print("==============================")
date = input("Silahkan isi: ")
print("")
a = BCA(user, pin, date)
b = a.mutasiTrx()
print(b)
