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
        th, td { text-align: center; padding: 4px, 8px; }
        table { border-width: 3px; border-collapse: collapse; }
  </style>
</head>
<body>

<A NAME="top"></A>
<table border="1">
<caption><strong>Locations</strong></caption>
  <tr valign="center">
	<th><strong>For</strong></th>
	<th><strong>Latitude</strong></th>
	<th><strong>Longitude</strong></th>
	<th><strong>UTC Offset</strong></th>
	<th><strong>DST</strong></th>
  </tr>

  <xsl:for-each select="/locations/location">
  <xsl:sort select="@for" />
  <tr>
    <td><xsl:value-of select="@for" /></td>
    <td><xsl:value-of select="@lat" /></td>
    <td><xsl:value-of select="@lon" /></td>
    <td><xsl:value-of select="@tz" /></td>
    <td>
    <xsl:choose>
        <xsl:when test="@obs=0">
            <xsl:text>No</xsl:text>
        </xsl:when>
        <xsl:otherwise>
            <xsl:text>Yes</xsl:text>
        </xsl:otherwise>
    </xsl:choose>
    </td>
   </tr>
  </xsl:for-each>
</table>

</body>
</html>
</xsl:template>
</xsl:stylesheet>
