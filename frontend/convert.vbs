Set objStream = CreateObject("ADODB.Stream")
objStream.CharSet = "utf-16le"
objStream.Open
objStream.LoadFromFile "app.js"
strData = objStream.ReadText
objStream.Close

Set objStream = CreateObject("ADODB.Stream")
objStream.CharSet = "utf-8"
objStream.Open
objStream.WriteText strData
objStream.SaveToFile "app.utf8.js", 2
objStream.Close

Set objStream = CreateObject("ADODB.Stream")
objStream.CharSet = "utf-16le"
objStream.Open
objStream.LoadFromFile "index.html"
strData = objStream.ReadText
objStream.Close

Set objStream = CreateObject("ADODB.Stream")
objStream.CharSet = "utf-8"
objStream.Open
objStream.WriteText strData
objStream.SaveToFile "index.utf8.html", 2
objStream.Close
