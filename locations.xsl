<?xml version="1.0" encoding="ISO-8859-1"?>
<xsl:stylesheet version="1.0"
   xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:template match="*">
   <xsl:apply-templates/>
</xsl:template>

<xsl:template match="text()">
   <xsl:value-of select="."/>
</xsl:template>

<xsl:template match="/">
<html>
<head> 
<title>Locations for sunrise/set</title>
  <style>
      .th { text-align: center; }
  </style>
</head>
<body>

<A NAME="top"></A>
<table border="1">
<caption><strong>Locations</strong></caption>
  <tr valign="center">
	<th><strong>For</strong></th>
	<th><strong>Lat</strong></th>
	<th><strong>Lon</strong></th>
	<th><strong>Time Zone</strong></th>
  </tr>

  <xsl:for-each select="/locations/location">
  <xsl:sort select="@for" />
  <tr>
    <td><xsl:value-of select="@for" /></td>
    <td><xsl:value-of select="@lat" /></td>
    <td><xsl:value-of select="@lon" /></td>
    <td><xsl:value-of select="@tz" /></td>
   </tr>
  </xsl:for-each>
</table>

</body>
</html>
</xsl:template>
</xsl:stylesheet>
