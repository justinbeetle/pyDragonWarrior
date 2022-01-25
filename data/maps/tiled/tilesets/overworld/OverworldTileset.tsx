<?xml version="1.0" encoding="UTF-8"?>
<tileset version="1.2" tiledversion="1.2.2" name="overworld" tilewidth="16" tileheight="16" tilecount="3200" columns="40">
 <image source="Overworld_Tileset.png" width="640" height="1280"/>
 <terraintypes>
  <terrain name="trees (object layer)" tile="286"/>
  <terrain name="regular grass" tile="1"/>
  <terrain name="light grass" tile="81"/>
  <terrain name="Hills" tile="161"/>
  <terrain name="cliffs" tile="481"/>
  <terrain name="ocean (upper layer)" tile="140"/>
  <terrain name="beach" tile="681"/>
  <terrain name="shallow ocean (under layer)" tile="826"/>
  <terrain name="ocean (under layer)" tile="801"/>
  <terrain name="deep ocean (under layer)" tile="896"/>
  <terrain name="swamp" tile="977"/>
  <terrain name="pine trees (object layer)" tile="698"/>
  <terrain name="village grass" tile="1640"/>
  <terrain name="village dirt" tile="1571"/>
  <terrain name="village path" tile="1576"/>
  <terrain name="village light grass" tile="1561"/>
 </terraintypes>
 <tile id="0" terrain="1,1,1,1">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="1" terrain="1,1,1,1" probability="0.25">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="2" terrain="1,1,1,1" probability="0.25">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="3">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="4">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="5">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="6">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="7">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="8">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="9">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="10">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="11">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="12">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="13">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="14">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="15">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="16">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="17">
  <properties>
   <property name="type" value="bridge"/>
  </properties>
 </tile>
 <tile id="18">
  <properties>
   <property name="type" value="bridge"/>
  </properties>
 </tile>
 <tile id="19">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="20">
  <properties>
   <property name="type" value="river"/>
  </properties>
  <animation>
   <frame tileid="20" duration="240"/>
   <frame tileid="24" duration="240"/>
   <frame tileid="28" duration="240"/>
   <frame tileid="32" duration="240"/>
  </animation>
 </tile>
 <tile id="21">
  <properties>
   <property name="type" value="river"/>
  </properties>
  <animation>
   <frame tileid="21" duration="240"/>
   <frame tileid="25" duration="240"/>
   <frame tileid="29" duration="240"/>
   <frame tileid="33" duration="240"/>
  </animation>
 </tile>
 <tile id="22">
  <properties>
   <property name="type" value="river"/>
  </properties>
  <animation>
   <frame tileid="22" duration="240"/>
   <frame tileid="26" duration="240"/>
   <frame tileid="30" duration="240"/>
   <frame tileid="34" duration="240"/>
  </animation>
 </tile>
 <tile id="23">
  <properties>
   <property name="type" value="river"/>
  </properties>
  <animation>
   <frame tileid="23" duration="240"/>
   <frame tileid="27" duration="240"/>
   <frame tileid="31" duration="240"/>
   <frame tileid="35" duration="240"/>
  </animation>
 </tile>
 <tile id="24">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="25">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="26">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="27">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="28">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="29">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="30">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="31">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="32">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="32" duration="240"/>
   <frame tileid="28" duration="240"/>
   <frame tileid="24" duration="240"/>
   <frame tileid="20" duration="240"/>
  </animation>
 </tile>
 <tile id="33">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="33" duration="240"/>
   <frame tileid="29" duration="240"/>
   <frame tileid="25" duration="240"/>
   <frame tileid="21" duration="240"/>
  </animation>
 </tile>
 <tile id="34">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="34" duration="240"/>
   <frame tileid="30" duration="240"/>
   <frame tileid="26" duration="240"/>
   <frame tileid="22" duration="240"/>
  </animation>
 </tile>
 <tile id="35">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="35" duration="240"/>
   <frame tileid="31" duration="240"/>
   <frame tileid="27" duration="240"/>
   <frame tileid="23" duration="240"/>
  </animation>
 </tile>
 <tile id="36">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="36" duration="240"/>
   <frame tileid="37" duration="240"/>
   <frame tileid="38" duration="240"/>
   <frame tileid="39" duration="240"/>
  </animation>
 </tile>
 <tile id="37">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="38">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="39">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="40" terrain="1,1,1,2">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="41" terrain="1,1,2,2">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="42" terrain="1,1,2,1">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="43" terrain="1,2,2,2">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="44" terrain="2,1,2,2">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="45" terrain="2,2,2,2" probability="0.1">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="46" terrain="2,2,2,2" probability="0.1">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="47">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="48">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="49">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="50">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="51">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="52">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="53">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="54">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="55">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="56">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="57">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="58">
  <properties>
   <property name="type" value="bridge"/>
  </properties>
 </tile>
 <tile id="59">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="60">
  <properties>
   <property name="type" value="river"/>
  </properties>
  <animation>
   <frame tileid="60" duration="240"/>
   <frame tileid="64" duration="240"/>
   <frame tileid="68" duration="240"/>
   <frame tileid="72" duration="240"/>
  </animation>
 </tile>
 <tile id="61">
  <properties>
   <property name="type" value="river"/>
  </properties>
  <animation>
   <frame tileid="61" duration="240"/>
   <frame tileid="65" duration="240"/>
   <frame tileid="69" duration="240"/>
   <frame tileid="73" duration="240"/>
  </animation>
 </tile>
 <tile id="62">
  <properties>
   <property name="type" value="river"/>
  </properties>
  <animation>
   <frame tileid="62" duration="240"/>
   <frame tileid="66" duration="240"/>
   <frame tileid="70" duration="240"/>
   <frame tileid="74" duration="240"/>
  </animation>
 </tile>
 <tile id="63">
  <properties>
   <property name="type" value="river"/>
  </properties>
  <animation>
   <frame tileid="63" duration="240"/>
   <frame tileid="67" duration="240"/>
   <frame tileid="71" duration="240"/>
   <frame tileid="75" duration="240"/>
  </animation>
 </tile>
 <tile id="64">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="65">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="66">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="67">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="68">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="69">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="70">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="71">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="72">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="72" duration="240"/>
   <frame tileid="68" duration="240"/>
   <frame tileid="64" duration="240"/>
   <frame tileid="60" duration="240"/>
  </animation>
 </tile>
 <tile id="73">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="73" duration="240"/>
   <frame tileid="69" duration="240"/>
   <frame tileid="65" duration="240"/>
   <frame tileid="61" duration="240"/>
  </animation>
 </tile>
 <tile id="74">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="74" duration="240"/>
   <frame tileid="70" duration="240"/>
   <frame tileid="66" duration="240"/>
   <frame tileid="62" duration="240"/>
  </animation>
 </tile>
 <tile id="75">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="75" duration="240"/>
   <frame tileid="71" duration="240"/>
   <frame tileid="67" duration="240"/>
   <frame tileid="63" duration="240"/>
  </animation>
 </tile>
 <tile id="76">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="76" duration="240"/>
   <frame tileid="77" duration="240"/>
   <frame tileid="78" duration="240"/>
   <frame tileid="79" duration="240"/>
  </animation>
 </tile>
 <tile id="77">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="78">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="79">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="80" terrain="1,2,1,2">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="81" terrain="2,2,2,2">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="82" terrain="2,1,2,1">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="83" terrain="2,2,1,2">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="84" terrain="2,2,2,1">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="85" terrain="2,2,2,2" probability="0.1">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="86" terrain="2,2,2,2" probability="0.1">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="87">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="88">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="89">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="90">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="91">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="92">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="93">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="94">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="95">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="96">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="97">
  <properties>
   <property name="type" value="bridge"/>
  </properties>
 </tile>
 <tile id="98">
  <properties>
   <property name="type" value="bridge"/>
  </properties>
 </tile>
 <tile id="99">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="100">
  <properties>
   <property name="type" value="river"/>
  </properties>
  <animation>
   <frame tileid="100" duration="240"/>
   <frame tileid="104" duration="240"/>
   <frame tileid="108" duration="240"/>
   <frame tileid="112" duration="240"/>
  </animation>
 </tile>
 <tile id="101">
  <properties>
   <property name="type" value="river_walkable"/>
  </properties>
  <animation>
   <frame tileid="101" duration="240"/>
   <frame tileid="105" duration="240"/>
   <frame tileid="109" duration="240"/>
   <frame tileid="113" duration="240"/>
  </animation>
 </tile>
 <tile id="102">
  <properties>
   <property name="type" value="river"/>
  </properties>
  <animation>
   <frame tileid="102" duration="240"/>
   <frame tileid="106" duration="240"/>
   <frame tileid="110" duration="240"/>
   <frame tileid="114" duration="240"/>
  </animation>
 </tile>
 <tile id="103">
  <properties>
   <property name="type" value="river_walkable"/>
  </properties>
  <animation>
   <frame tileid="103" duration="240"/>
   <frame tileid="107" duration="240"/>
   <frame tileid="111" duration="240"/>
   <frame tileid="115" duration="240"/>
  </animation>
 </tile>
 <tile id="104">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="105">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="106">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="107">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="108">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="109">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="110">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="111">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="112">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="112" duration="240"/>
   <frame tileid="108" duration="240"/>
   <frame tileid="104" duration="240"/>
   <frame tileid="100" duration="240"/>
  </animation>
 </tile>
 <tile id="113">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="113" duration="240"/>
   <frame tileid="109" duration="240"/>
   <frame tileid="105" duration="240"/>
   <frame tileid="101" duration="240"/>
  </animation>
 </tile>
 <tile id="114">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="114" duration="240"/>
   <frame tileid="110" duration="240"/>
   <frame tileid="106" duration="240"/>
   <frame tileid="102" duration="240"/>
  </animation>
 </tile>
 <tile id="115">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="115" duration="240"/>
   <frame tileid="111" duration="240"/>
   <frame tileid="107" duration="240"/>
   <frame tileid="103" duration="240"/>
  </animation>
 </tile>
 <tile id="116">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="116" duration="240"/>
   <frame tileid="117" duration="240"/>
   <frame tileid="118" duration="240"/>
   <frame tileid="119" duration="240"/>
  </animation>
 </tile>
 <tile id="117">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="118">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="119">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="120" terrain="1,2,1,1">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="121" terrain="2,2,1,1">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="122" terrain="2,1,1,1">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="123" terrain="1,2,2,1">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="124" terrain="2,1,1,2">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="125">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="126">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="127">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="128">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="129">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="130">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="131">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="132">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="133">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="134">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="135">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="136">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="137">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="138">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="139">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="140">
  <properties>
   <property name="type" value="river"/>
  </properties>
  <animation>
   <frame tileid="140" duration="240"/>
   <frame tileid="144" duration="240"/>
   <frame tileid="148" duration="240"/>
   <frame tileid="152" duration="240"/>
  </animation>
 </tile>
 <tile id="141">
  <properties>
   <property name="type" value="river"/>
  </properties>
  <animation>
   <frame tileid="141" duration="240"/>
   <frame tileid="145" duration="240"/>
   <frame tileid="149" duration="240"/>
   <frame tileid="153" duration="240"/>
  </animation>
 </tile>
 <tile id="142">
  <properties>
   <property name="type" value="river"/>
  </properties>
  <animation>
   <frame tileid="142" duration="240"/>
   <frame tileid="146" duration="240"/>
   <frame tileid="150" duration="240"/>
   <frame tileid="154" duration="240"/>
  </animation>
 </tile>
 <tile id="143">
  <properties>
   <property name="type" value="river"/>
  </properties>
  <animation>
   <frame tileid="143" duration="240"/>
   <frame tileid="147" duration="240"/>
   <frame tileid="151" duration="240"/>
   <frame tileid="155" duration="240"/>
  </animation>
 </tile>
 <tile id="144">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="145">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="146">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="147">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="148">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="149">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="150">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="151">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="152">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="153">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="153" duration="240"/>
   <frame tileid="149" duration="240"/>
   <frame tileid="145" duration="240"/>
   <frame tileid="141" duration="240"/>
  </animation>
 </tile>
 <tile id="154">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="154" duration="240"/>
   <frame tileid="150" duration="240"/>
   <frame tileid="146" duration="240"/>
   <frame tileid="142" duration="240"/>
  </animation>
 </tile>
 <tile id="155">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="155" duration="240"/>
   <frame tileid="151" duration="240"/>
   <frame tileid="147" duration="240"/>
   <frame tileid="143" duration="240"/>
  </animation>
 </tile>
 <tile id="156">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="156" duration="240"/>
   <frame tileid="157" duration="240"/>
   <frame tileid="158" duration="240"/>
   <frame tileid="159" duration="240"/>
  </animation>
 </tile>
 <tile id="157">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="158">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="159">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="160" terrain="1,1,1,3">
  <properties>
   <property name="type" value="hill"/>
  </properties>
 </tile>
 <tile id="161" terrain="1,1,3,3">
  <properties>
   <property name="type" value="hill"/>
  </properties>
 </tile>
 <tile id="162" terrain="1,1,3,1">
  <properties>
   <property name="type" value="hill"/>
  </properties>
 </tile>
 <tile id="163">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="164">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="165">
  <properties>
   <property name="type" value="mountain"/>
  </properties>
 </tile>
 <tile id="166">
  <properties>
   <property name="type" value="mountain"/>
  </properties>
 </tile>
 <tile id="167">
  <properties>
   <property name="type" value="mountain"/>
  </properties>
 </tile>
 <tile id="168">
  <properties>
   <property name="type" value="mountain"/>
  </properties>
 </tile>
 <tile id="169">
  <properties>
   <property name="type" value="mountain"/>
  </properties>
 </tile>
 <tile id="170">
  <properties>
   <property name="type" value="mountain"/>
  </properties>
 </tile>
 <tile id="171">
  <properties>
   <property name="type" value="mountain"/>
  </properties>
 </tile>
 <tile id="172">
  <properties>
   <property name="type" value="mountain"/>
  </properties>
 </tile>
 <tile id="173">
  <properties>
   <property name="type" value="mountain"/>
  </properties>
 </tile>
 <tile id="174">
  <properties>
   <property name="type" value="mountain"/>
  </properties>
 </tile>
 <tile id="175">
  <properties>
   <property name="type" value="mountain"/>
  </properties>
 </tile>
 <tile id="176">
  <properties>
   <property name="type" value="cliff"/>
  </properties>
 </tile>
 <tile id="177">
  <properties>
   <property name="type" value="bridge"/>
  </properties>
 </tile>
 <tile id="178">
  <properties>
   <property name="type" value="bridge"/>
  </properties>
 </tile>
 <tile id="179">
  <properties>
   <property name="type" value="bridge"/>
  </properties>
 </tile>
 <tile id="180" terrain="5,5,4,1">
  <properties>
   <property name="type" value="shore_cliff"/>
  </properties>
  <animation>
   <frame tileid="180" duration="240"/>
   <frame tileid="184" duration="240"/>
   <frame tileid="188" duration="240"/>
   <frame tileid="192" duration="240"/>
   <frame tileid="188" duration="240"/>
   <frame tileid="184" duration="240"/>
  </animation>
 </tile>
 <tile id="181" terrain="5,5,1,4">
  <properties>
   <property name="type" value="shore_cliff"/>
  </properties>
  <animation>
   <frame tileid="181" duration="240"/>
   <frame tileid="185" duration="240"/>
   <frame tileid="189" duration="240"/>
   <frame tileid="193" duration="240"/>
   <frame tileid="189" duration="240"/>
   <frame tileid="185" duration="240"/>
  </animation>
 </tile>
 <tile id="182" terrain="5,4,5,1">
  <properties>
   <property name="type" value="shore_cliff"/>
  </properties>
  <animation>
   <frame tileid="182" duration="240"/>
   <frame tileid="186" duration="240"/>
   <frame tileid="190" duration="240"/>
   <frame tileid="194" duration="240"/>
   <frame tileid="190" duration="240"/>
   <frame tileid="186" duration="240"/>
  </animation>
 </tile>
 <tile id="183" terrain="4,5,1,5">
  <properties>
   <property name="type" value="shore_cliff"/>
  </properties>
  <animation>
   <frame tileid="183" duration="240"/>
   <frame tileid="187" duration="240"/>
   <frame tileid="191" duration="240"/>
   <frame tileid="195" duration="240"/>
   <frame tileid="191" duration="240"/>
   <frame tileid="187" duration="240"/>
  </animation>
 </tile>
 <tile id="184">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="185">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="186">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="187">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="188">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="189">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="190">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="191">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="192">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="193">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="194">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="195">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="196">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="196" duration="240"/>
   <frame tileid="197" duration="240"/>
   <frame tileid="198" duration="240"/>
   <frame tileid="199" duration="240"/>
  </animation>
 </tile>
 <tile id="197">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="198">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="199">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="200" terrain="1,3,1,3">
  <properties>
   <property name="type" value="hill"/>
  </properties>
 </tile>
 <tile id="201" terrain="3,3,3,3">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="202" terrain="3,1,3,1">
  <properties>
   <property name="type" value="hill"/>
  </properties>
 </tile>
 <tile id="203">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="204">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="205">
  <properties>
   <property name="type" value="mountain"/>
  </properties>
 </tile>
 <tile id="206">
  <properties>
   <property name="type" value="mountain"/>
  </properties>
 </tile>
 <tile id="207">
  <properties>
   <property name="type" value="mountain"/>
  </properties>
 </tile>
 <tile id="208">
  <properties>
   <property name="type" value="mountain"/>
  </properties>
 </tile>
 <tile id="209">
  <properties>
   <property name="type" value="mountain"/>
  </properties>
 </tile>
 <tile id="210">
  <properties>
   <property name="type" value="mountain"/>
  </properties>
 </tile>
 <tile id="211">
  <properties>
   <property name="type" value="mountain"/>
  </properties>
 </tile>
 <tile id="212">
  <properties>
   <property name="type" value="mountain"/>
  </properties>
 </tile>
 <tile id="213">
  <properties>
   <property name="type" value="mountain"/>
  </properties>
 </tile>
 <tile id="214">
  <properties>
   <property name="type" value="mountain"/>
  </properties>
 </tile>
 <tile id="215">
  <properties>
   <property name="type" value="mountain"/>
  </properties>
 </tile>
 <tile id="216">
  <properties>
   <property name="type" value="cliff"/>
  </properties>
 </tile>
 <tile id="217">
  <properties>
   <property name="type" value="cliff"/>
  </properties>
 </tile>
 <tile id="218">
  <properties>
   <property name="type" value="cliff"/>
  </properties>
 </tile>
 <tile id="219">
  <properties>
   <property name="type" value="cliff"/>
  </properties>
 </tile>
 <tile id="220" terrain="4,1,5,5">
  <properties>
   <property name="type" value="shore_cliff"/>
  </properties>
  <animation>
   <frame tileid="220" duration="240"/>
   <frame tileid="224" duration="240"/>
   <frame tileid="228" duration="240"/>
   <frame tileid="232" duration="240"/>
   <frame tileid="228" duration="240"/>
   <frame tileid="224" duration="240"/>
  </animation>
 </tile>
 <tile id="221" terrain="1,4,5,5">
  <properties>
   <property name="type" value="shore_cliff"/>
  </properties>
  <animation>
   <frame tileid="221" duration="240"/>
   <frame tileid="225" duration="240"/>
   <frame tileid="229" duration="240"/>
   <frame tileid="233" duration="240"/>
   <frame tileid="229" duration="240"/>
   <frame tileid="225" duration="240"/>
  </animation>
 </tile>
 <tile id="222" terrain="5,1,5,4">
  <properties>
   <property name="type" value="shore_cliff"/>
  </properties>
  <animation>
   <frame tileid="222" duration="240"/>
   <frame tileid="226" duration="240"/>
   <frame tileid="230" duration="240"/>
   <frame tileid="234" duration="240"/>
   <frame tileid="230" duration="240"/>
   <frame tileid="226" duration="240"/>
  </animation>
 </tile>
 <tile id="223" terrain="1,5,4,5">
  <properties>
   <property name="type" value="shore_cliff"/>
  </properties>
  <animation>
   <frame tileid="223" duration="240"/>
   <frame tileid="227" duration="240"/>
   <frame tileid="231" duration="240"/>
   <frame tileid="235" duration="240"/>
   <frame tileid="231" duration="240"/>
   <frame tileid="227" duration="240"/>
  </animation>
 </tile>
 <tile id="224">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="225">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="226">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="227">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="228">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="229">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="230">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="231">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="232">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="233">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="234">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="235">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="236">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="236" duration="240"/>
   <frame tileid="237" duration="240"/>
   <frame tileid="238" duration="240"/>
   <frame tileid="239" duration="240"/>
  </animation>
 </tile>
 <tile id="237">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="238">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="239">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="240" terrain="1,3,1,1">
  <properties>
   <property name="type" value="hill"/>
  </properties>
 </tile>
 <tile id="241" terrain="3,3,1,1">
  <properties>
   <property name="type" value="hill"/>
  </properties>
 </tile>
 <tile id="242" terrain="3,1,1,1">
  <properties>
   <property name="type" value="hill"/>
  </properties>
 </tile>
 <tile id="243">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="244">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="245">
  <properties>
   <property name="type" value="mountain"/>
  </properties>
 </tile>
 <tile id="246">
  <properties>
   <property name="type" value="mountain"/>
  </properties>
 </tile>
 <tile id="247">
  <properties>
   <property name="type" value="mountain"/>
  </properties>
 </tile>
 <tile id="248">
  <properties>
   <property name="type" value="mountain"/>
  </properties>
 </tile>
 <tile id="249">
  <properties>
   <property name="type" value="mountain"/>
  </properties>
 </tile>
 <tile id="250">
  <properties>
   <property name="type" value="mountain"/>
  </properties>
 </tile>
 <tile id="251">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="252">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="253">
  <properties>
   <property name="type" value="mountain"/>
  </properties>
 </tile>
 <tile id="254">
  <properties>
   <property name="type" value="mountain"/>
  </properties>
 </tile>
 <tile id="255">
  <properties>
   <property name="type" value="mountain"/>
  </properties>
 </tile>
 <tile id="256">
  <properties>
   <property name="type" value="cliff"/>
  </properties>
 </tile>
 <tile id="257">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="258">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="259">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="260" terrain="5,5,4,6">
  <properties>
   <property name="type" value="shore_cliff"/>
  </properties>
  <animation>
   <frame tileid="260" duration="240"/>
   <frame tileid="264" duration="240"/>
   <frame tileid="268" duration="240"/>
   <frame tileid="272" duration="240"/>
   <frame tileid="268" duration="240"/>
   <frame tileid="264" duration="240"/>
  </animation>
 </tile>
 <tile id="261" terrain="5,5,6,4">
  <properties>
   <property name="type" value="shore_cliff"/>
  </properties>
  <animation>
   <frame tileid="261" duration="240"/>
   <frame tileid="265" duration="240"/>
   <frame tileid="269" duration="240"/>
   <frame tileid="273" duration="240"/>
   <frame tileid="269" duration="240"/>
   <frame tileid="265" duration="240"/>
  </animation>
 </tile>
 <tile id="262" terrain="5,4,5,6">
  <properties>
   <property name="type" value="shore_cliff"/>
  </properties>
  <animation>
   <frame tileid="262" duration="240"/>
   <frame tileid="266" duration="240"/>
   <frame tileid="270" duration="240"/>
   <frame tileid="274" duration="240"/>
   <frame tileid="270" duration="240"/>
   <frame tileid="266" duration="240"/>
  </animation>
 </tile>
 <tile id="263" terrain="4,5,6,5">
  <properties>
   <property name="type" value="shore_cliff"/>
  </properties>
  <animation>
   <frame tileid="263" duration="240"/>
   <frame tileid="267" duration="240"/>
   <frame tileid="271" duration="240"/>
   <frame tileid="275" duration="240"/>
   <frame tileid="271" duration="240"/>
   <frame tileid="267" duration="240"/>
  </animation>
 </tile>
 <tile id="264">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="265">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="266">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="267">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="268">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="269">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="270">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="271">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="272">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="273">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="274">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="275">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="276">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="277">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="278">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="279">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="280" terrain=",,,0">
  <properties>
   <property name="type" value="deciduous_forest"/>
  </properties>
 </tile>
 <tile id="281" terrain=",,0,0">
  <properties>
   <property name="type" value="deciduous_forest"/>
  </properties>
 </tile>
 <tile id="282" terrain=",,0,">
  <properties>
   <property name="type" value="deciduous_forest"/>
  </properties>
 </tile>
 <tile id="283" terrain=",0,0,0">
  <properties>
   <property name="type" value="deciduous_forest"/>
  </properties>
 </tile>
 <tile id="284" terrain="0,,0,0">
  <properties>
   <property name="type" value="deciduous_forest"/>
  </properties>
 </tile>
 <tile id="285" terrain="0,0,0,0" probability="0.5">
  <properties>
   <property name="type" value="deciduous_forest"/>
  </properties>
 </tile>
 <tile id="286">
  <properties>
   <property name="type" value="deciduous_forest"/>
  </properties>
 </tile>
 <tile id="287">
  <properties>
   <property name="type" value="mountain"/>
  </properties>
 </tile>
 <tile id="288">
  <properties>
   <property name="type" value="mountain"/>
  </properties>
 </tile>
 <tile id="289">
  <properties>
   <property name="type" value="mountain"/>
  </properties>
 </tile>
 <tile id="290">
  <properties>
   <property name="type" value="mountain"/>
  </properties>
 </tile>
 <tile id="291">
  <properties>
   <property name="type" value="mountain"/>
  </properties>
 </tile>
 <tile id="292">
  <properties>
   <property name="type" value="mountain"/>
  </properties>
 </tile>
 <tile id="293">
  <properties>
   <property name="type" value="mountain"/>
  </properties>
 </tile>
 <tile id="294">
  <properties>
   <property name="type" value="mountain"/>
  </properties>
 </tile>
 <tile id="295">
  <properties>
   <property name="type" value="mountain"/>
  </properties>
 </tile>
 <tile id="296">
  <properties>
   <property name="type" value="mountain"/>
  </properties>
 </tile>
 <tile id="297">
  <properties>
   <property name="type" value="mountain"/>
  </properties>
 </tile>
 <tile id="298">
  <properties>
   <property name="type" value="mountain"/>
  </properties>
 </tile>
 <tile id="299">
  <properties>
   <property name="type" value="mountain"/>
  </properties>
 </tile>
 <tile id="300" terrain="4,6,5,5">
  <properties>
   <property name="type" value="shore_cliff"/>
  </properties>
  <animation>
   <frame tileid="300" duration="240"/>
   <frame tileid="304" duration="240"/>
   <frame tileid="308" duration="240"/>
   <frame tileid="312" duration="240"/>
   <frame tileid="308" duration="240"/>
   <frame tileid="304" duration="240"/>
  </animation>
 </tile>
 <tile id="301" terrain="6,4,5,5">
  <properties>
   <property name="type" value="shore_cliff"/>
  </properties>
  <animation>
   <frame tileid="301" duration="240"/>
   <frame tileid="305" duration="240"/>
   <frame tileid="309" duration="240"/>
   <frame tileid="313" duration="240"/>
   <frame tileid="309" duration="240"/>
   <frame tileid="305" duration="240"/>
  </animation>
 </tile>
 <tile id="302" terrain="5,6,5,4">
  <properties>
   <property name="type" value="shore_cliff"/>
  </properties>
  <animation>
   <frame tileid="302" duration="240"/>
   <frame tileid="306" duration="240"/>
   <frame tileid="310" duration="240"/>
   <frame tileid="314" duration="240"/>
   <frame tileid="310" duration="240"/>
   <frame tileid="306" duration="240"/>
  </animation>
 </tile>
 <tile id="303" terrain="6,5,4,5">
  <properties>
   <property name="type" value="shore_cliff"/>
  </properties>
  <animation>
   <frame tileid="303" duration="240"/>
   <frame tileid="307" duration="240"/>
   <frame tileid="311" duration="240"/>
   <frame tileid="315" duration="240"/>
   <frame tileid="311" duration="240"/>
   <frame tileid="307" duration="240"/>
  </animation>
 </tile>
 <tile id="304">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="305">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="306">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="307">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="308">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="309">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="310">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="311">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="312">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="313">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="314">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="315">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="316">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="317">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="318">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="319">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="320" terrain=",0,,0">
  <properties>
   <property name="type" value="deciduous_forest"/>
  </properties>
 </tile>
 <tile id="321" terrain="0,0,0,0">
  <properties>
   <property name="type" value="deciduous_forest"/>
  </properties>
 </tile>
 <tile id="322" terrain="0,,0,">
  <properties>
   <property name="type" value="deciduous_forest"/>
  </properties>
 </tile>
 <tile id="323" terrain="0,0,,0">
  <properties>
   <property name="type" value="deciduous_forest"/>
  </properties>
 </tile>
 <tile id="324" terrain="0,0,0,">
  <properties>
   <property name="type" value="deciduous_forest"/>
  </properties>
 </tile>
 <tile id="325" terrain="0,0,0,0" probability="0.5">
  <properties>
   <property name="type" value="deciduous_forest"/>
  </properties>
 </tile>
 <tile id="326">
  <properties>
   <property name="type" value="deciduous_forest"/>
  </properties>
 </tile>
 <tile id="327">
  <properties>
   <property name="type" value="mountain"/>
  </properties>
 </tile>
 <tile id="328">
  <properties>
   <property name="type" value="mountain"/>
  </properties>
 </tile>
 <tile id="329">
  <properties>
   <property name="type" value="mountain"/>
  </properties>
 </tile>
 <tile id="330">
  <properties>
   <property name="type" value="mountain"/>
  </properties>
 </tile>
 <tile id="331">
  <properties>
   <property name="type" value="mountain"/>
  </properties>
 </tile>
 <tile id="332">
  <properties>
   <property name="type" value="mountain"/>
  </properties>
 </tile>
 <tile id="333">
  <properties>
   <property name="type" value="mountain"/>
  </properties>
 </tile>
 <tile id="334">
  <properties>
   <property name="type" value="mountain"/>
  </properties>
 </tile>
 <tile id="335">
  <properties>
   <property name="type" value="mountain"/>
  </properties>
 </tile>
 <tile id="336">
  <properties>
   <property name="type" value="mountain"/>
  </properties>
 </tile>
 <tile id="337">
  <properties>
   <property name="type" value="mountain"/>
  </properties>
 </tile>
 <tile id="338">
  <properties>
   <property name="type" value="mountain"/>
  </properties>
 </tile>
 <tile id="339">
  <properties>
   <property name="type" value="mountain"/>
  </properties>
 </tile>
 <tile id="340" terrain="5,5,1,6">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="340" duration="240"/>
   <frame tileid="344" duration="240"/>
   <frame tileid="348" duration="240"/>
   <frame tileid="352" duration="240"/>
   <frame tileid="348" duration="240"/>
   <frame tileid="344" duration="240"/>
  </animation>
 </tile>
 <tile id="341" terrain="5,5,6,1">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="341" duration="240"/>
   <frame tileid="345" duration="240"/>
   <frame tileid="349" duration="240"/>
   <frame tileid="353" duration="240"/>
   <frame tileid="349" duration="240"/>
   <frame tileid="345" duration="240"/>
  </animation>
 </tile>
 <tile id="342" terrain="5,1,5,6">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="342" duration="240"/>
   <frame tileid="346" duration="240"/>
   <frame tileid="350" duration="240"/>
   <frame tileid="354" duration="240"/>
   <frame tileid="350" duration="240"/>
   <frame tileid="346" duration="240"/>
  </animation>
 </tile>
 <tile id="343" terrain="1,5,6,5">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="343" duration="240"/>
   <frame tileid="347" duration="240"/>
   <frame tileid="351" duration="240"/>
   <frame tileid="355" duration="240"/>
   <frame tileid="351" duration="240"/>
   <frame tileid="347" duration="240"/>
  </animation>
 </tile>
 <tile id="344">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="345">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="346">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="347">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="348">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="349">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="350">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="351">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="352">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="353">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="354">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="355">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="356">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="356" duration="240"/>
   <frame tileid="357" duration="240"/>
   <frame tileid="358" duration="240"/>
   <frame tileid="359" duration="240"/>
   <frame tileid="358" duration="240"/>
   <frame tileid="357" duration="240"/>
  </animation>
 </tile>
 <tile id="357">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="358">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="359">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="360" terrain=",0,,">
  <properties>
   <property name="type" value="deciduous_forest"/>
  </properties>
 </tile>
 <tile id="361" terrain="0,0,,">
  <properties>
   <property name="type" value="deciduous_forest"/>
  </properties>
 </tile>
 <tile id="362" terrain="0,,,">
  <properties>
   <property name="type" value="deciduous_forest"/>
  </properties>
 </tile>
 <tile id="363" terrain=",0,0,">
  <properties>
   <property name="type" value="deciduous_forest"/>
  </properties>
 </tile>
 <tile id="364" terrain="0,,,0">
  <properties>
   <property name="type" value="deciduous_forest"/>
  </properties>
 </tile>
 <tile id="365" terrain=",4,,">
  <properties>
   <property name="type" value="cliff"/>
  </properties>
 </tile>
 <tile id="366" terrain="4,,,">
  <properties>
   <property name="type" value="cliff"/>
  </properties>
 </tile>
 <tile id="367">
  <properties>
   <property name="type" value="mountain"/>
  </properties>
 </tile>
 <tile id="368">
  <properties>
   <property name="type" value="mountain"/>
  </properties>
 </tile>
 <tile id="369">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="370">
  <properties>
   <property name="type" value="mountain"/>
  </properties>
 </tile>
 <tile id="371">
  <properties>
   <property name="type" value="mountain"/>
  </properties>
 </tile>
 <tile id="372">
  <properties>
   <property name="type" value="mountain"/>
  </properties>
 </tile>
 <tile id="373">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="374">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="375">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="376">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="377">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="378">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="379">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="380" terrain="1,6,5,5">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="380" duration="240"/>
   <frame tileid="384" duration="240"/>
   <frame tileid="388" duration="240"/>
   <frame tileid="392" duration="240"/>
   <frame tileid="388" duration="240"/>
   <frame tileid="384" duration="240"/>
  </animation>
 </tile>
 <tile id="381" terrain="6,1,5,5">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="381" duration="240"/>
   <frame tileid="385" duration="240"/>
   <frame tileid="389" duration="240"/>
   <frame tileid="393" duration="240"/>
   <frame tileid="389" duration="240"/>
   <frame tileid="385" duration="240"/>
  </animation>
 </tile>
 <tile id="382" terrain="5,6,5,1">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="382" duration="240"/>
   <frame tileid="386" duration="240"/>
   <frame tileid="390" duration="240"/>
   <frame tileid="394" duration="240"/>
   <frame tileid="390" duration="240"/>
   <frame tileid="386" duration="240"/>
  </animation>
 </tile>
 <tile id="383" terrain="6,5,1,5">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="383" duration="240"/>
   <frame tileid="387" duration="240"/>
   <frame tileid="391" duration="240"/>
   <frame tileid="395" duration="240"/>
   <frame tileid="391" duration="240"/>
   <frame tileid="387" duration="240"/>
  </animation>
 </tile>
 <tile id="384">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="385">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="386">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="387">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="388">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="389">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="390">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="391">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="392">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="393">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="394">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="395">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="396">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="396" duration="240"/>
   <frame tileid="397" duration="240"/>
   <frame tileid="398" duration="240"/>
   <frame tileid="399" duration="240"/>
   <frame tileid="398" duration="240"/>
   <frame tileid="397" duration="240"/>
  </animation>
 </tile>
 <tile id="397">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="398">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="399">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="400" terrain="1,1,1,4">
  <properties>
   <property name="type" value="cliff"/>
  </properties>
 </tile>
 <tile id="401" terrain="1,1,4,4">
  <properties>
   <property name="type" value="cliff"/>
  </properties>
 </tile>
 <tile id="402" terrain="1,1,4,1">
  <properties>
   <property name="type" value="cliff"/>
  </properties>
 </tile>
 <tile id="403" terrain="1,4,4,4">
  <properties>
   <property name="type" value="cliff_walkable"/>
  </properties>
 </tile>
 <tile id="404" terrain="4,1,4,4">
  <properties>
   <property name="type" value="cliff_walkable"/>
  </properties>
 </tile>
 <tile id="405">
  <properties>
   <property name="type" value="cliff"/>
  </properties>
 </tile>
 <tile id="406">
  <properties>
   <property name="type" value="cliff"/>
  </properties>
 </tile>
 <tile id="407">
  <properties>
   <property name="type" value="walls"/>
  </properties>
 </tile>
 <tile id="408">
  <properties>
   <property name="type" value="walls"/>
  </properties>
 </tile>
 <tile id="409">
  <properties>
   <property name="type" value="walls"/>
  </properties>
 </tile>
 <tile id="410">
  <properties>
   <property name="type" value="walls"/>
  </properties>
 </tile>
 <tile id="411">
  <properties>
   <property name="type" value="walls"/>
  </properties>
 </tile>
 <tile id="412">
  <properties>
   <property name="type" value="walls"/>
  </properties>
 </tile>
 <tile id="413">
  <properties>
   <property name="type" value="walls"/>
  </properties>
 </tile>
 <tile id="414">
  <properties>
   <property name="type" value="walls"/>
  </properties>
 </tile>
 <tile id="415">
  <properties>
   <property name="type" value="walls"/>
  </properties>
 </tile>
 <tile id="416">
  <properties>
   <property name="type" value="walls"/>
  </properties>
 </tile>
 <tile id="417">
  <properties>
   <property name="type" value="walls"/>
  </properties>
 </tile>
 <tile id="418">
  <properties>
   <property name="type" value="walls"/>
  </properties>
 </tile>
 <tile id="419">
  <properties>
   <property name="type" value="walls"/>
  </properties>
 </tile>
 <tile id="420" terrain="1,1,1,5">
  <properties>
   <property name="type" value="shore"/>
  </properties>
  <animation>
   <frame tileid="420" duration="240"/>
   <frame tileid="425" duration="240"/>
   <frame tileid="430" duration="240"/>
   <frame tileid="435" duration="240"/>
   <frame tileid="430" duration="240"/>
   <frame tileid="425" duration="240"/>
  </animation>
 </tile>
 <tile id="421" terrain="1,1,5,5">
  <properties>
   <property name="type" value="shore"/>
  </properties>
  <animation>
   <frame tileid="421" duration="240"/>
   <frame tileid="426" duration="240"/>
   <frame tileid="431" duration="240"/>
   <frame tileid="436" duration="240"/>
   <frame tileid="431" duration="240"/>
   <frame tileid="426" duration="240"/>
  </animation>
 </tile>
 <tile id="422" terrain="1,1,5,1">
  <properties>
   <property name="type" value="shore"/>
  </properties>
  <animation>
   <frame tileid="422" duration="240"/>
   <frame tileid="427" duration="240"/>
   <frame tileid="432" duration="240"/>
   <frame tileid="437" duration="240"/>
   <frame tileid="432" duration="240"/>
   <frame tileid="427" duration="240"/>
  </animation>
 </tile>
 <tile id="423" terrain="1,5,5,5">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="423" duration="240"/>
   <frame tileid="428" duration="240"/>
   <frame tileid="433" duration="240"/>
   <frame tileid="438" duration="240"/>
   <frame tileid="433" duration="240"/>
   <frame tileid="428" duration="240"/>
  </animation>
 </tile>
 <tile id="424" terrain="5,1,5,5">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="424" duration="240"/>
   <frame tileid="429" duration="240"/>
   <frame tileid="434" duration="240"/>
   <frame tileid="439" duration="240"/>
   <frame tileid="434" duration="240"/>
   <frame tileid="429" duration="240"/>
  </animation>
 </tile>
 <tile id="425">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="426">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="427">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="428">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="429">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="430">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="431">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="432">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="433">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="434">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="435">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="436">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="437">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="438">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="439">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="440" terrain="1,4,1,4">
  <properties>
   <property name="type" value="cliff"/>
  </properties>
 </tile>
 <tile id="441" terrain="4,4,4,4">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="442" terrain="4,1,4,1">
  <properties>
   <property name="type" value="cliff"/>
  </properties>
 </tile>
 <tile id="443" terrain="4,4,1,4">
  <properties>
   <property name="type" value="cliff"/>
  </properties>
 </tile>
 <tile id="444" terrain="4,4,4,1">
  <properties>
   <property name="type" value="cliff"/>
  </properties>
 </tile>
 <tile id="445">
  <properties>
   <property name="type" value="cliff"/>
  </properties>
 </tile>
 <tile id="446">
  <properties>
   <property name="type" value="cliff"/>
  </properties>
 </tile>
 <tile id="447">
  <properties>
   <property name="type" value="walls"/>
  </properties>
 </tile>
 <tile id="448">
  <properties>
   <property name="type" value="walls"/>
  </properties>
 </tile>
 <tile id="449">
  <properties>
   <property name="type" value="walls"/>
  </properties>
 </tile>
 <tile id="450">
  <properties>
   <property name="type" value="walls"/>
  </properties>
 </tile>
 <tile id="451">
  <properties>
   <property name="type" value="walls"/>
  </properties>
 </tile>
 <tile id="452">
  <properties>
   <property name="type" value="walls"/>
  </properties>
 </tile>
 <tile id="453">
  <properties>
   <property name="type" value="walls"/>
  </properties>
 </tile>
 <tile id="454">
  <properties>
   <property name="type" value="walls"/>
  </properties>
 </tile>
 <tile id="455">
  <properties>
   <property name="type" value="walls"/>
  </properties>
 </tile>
 <tile id="456">
  <properties>
   <property name="type" value="walls"/>
  </properties>
 </tile>
 <tile id="457">
  <properties>
   <property name="type" value="walls"/>
  </properties>
 </tile>
 <tile id="458">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="459">
  <properties>
   <property name="type" value="walls"/>
  </properties>
 </tile>
 <tile id="460" terrain="1,5,1,5">
  <properties>
   <property name="type" value="shore"/>
  </properties>
  <animation>
   <frame tileid="460" duration="240"/>
   <frame tileid="465" duration="240"/>
   <frame tileid="470" duration="240"/>
   <frame tileid="475" duration="240"/>
   <frame tileid="470" duration="240"/>
   <frame tileid="465" duration="240"/>
  </animation>
 </tile>
 <tile id="461" terrain="5,5,5,5">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="462" terrain="5,1,5,1">
  <properties>
   <property name="type" value="shore"/>
  </properties>
  <animation>
   <frame tileid="462" duration="240"/>
   <frame tileid="467" duration="240"/>
   <frame tileid="472" duration="240"/>
   <frame tileid="477" duration="240"/>
   <frame tileid="472" duration="240"/>
   <frame tileid="467" duration="240"/>
  </animation>
 </tile>
 <tile id="463" terrain="5,5,1,5">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="463" duration="240"/>
   <frame tileid="468" duration="240"/>
   <frame tileid="473" duration="240"/>
   <frame tileid="478" duration="240"/>
   <frame tileid="473" duration="240"/>
   <frame tileid="468" duration="240"/>
  </animation>
 </tile>
 <tile id="464" terrain="5,5,5,1">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="464" duration="240"/>
   <frame tileid="469" duration="240"/>
   <frame tileid="474" duration="240"/>
   <frame tileid="479" duration="240"/>
   <frame tileid="474" duration="240"/>
   <frame tileid="469" duration="240"/>
  </animation>
 </tile>
 <tile id="465">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="466">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="467">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="468">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="469">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="470">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="471">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="472">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="473">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="474">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="475">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="476">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="477">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="478">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="479">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="480" terrain="1,4,1,1">
  <properties>
   <property name="type" value="cliff"/>
  </properties>
 </tile>
 <tile id="481" terrain="4,4,1,1">
  <properties>
   <property name="type" value="cliff"/>
  </properties>
 </tile>
 <tile id="482" terrain="4,1,1,1">
  <properties>
   <property name="type" value="cliff"/>
  </properties>
 </tile>
 <tile id="483" terrain="1,4,4,1">
  <properties>
   <property name="type" value="cliff"/>
  </properties>
 </tile>
 <tile id="484" terrain="4,1,1,4">
  <properties>
   <property name="type" value="cliff"/>
  </properties>
 </tile>
 <tile id="485">
  <properties>
   <property name="type" value="cliff"/>
  </properties>
 </tile>
 <tile id="486">
  <properties>
   <property name="type" value="cliff"/>
  </properties>
 </tile>
 <tile id="487">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="488">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="489">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="490">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="491">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="492">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="493">
  <properties>
   <property name="type" value="walls"/>
  </properties>
 </tile>
 <tile id="494">
  <properties>
   <property name="type" value="walls"/>
  </properties>
 </tile>
 <tile id="495">
  <properties>
   <property name="type" value="walls"/>
  </properties>
 </tile>
 <tile id="496">
  <properties>
   <property name="type" value="walls"/>
  </properties>
 </tile>
 <tile id="497">
  <properties>
   <property name="type" value="walls"/>
  </properties>
 </tile>
 <tile id="498">
  <properties>
   <property name="type" value="gate"/>
  </properties>
 </tile>
 <tile id="499">
  <properties>
   <property name="type" value="walls"/>
  </properties>
 </tile>
 <tile id="500" terrain="1,5,1,1">
  <properties>
   <property name="type" value="shore_walkable"/>
  </properties>
  <animation>
   <frame tileid="500" duration="240"/>
   <frame tileid="505" duration="240"/>
   <frame tileid="510" duration="240"/>
   <frame tileid="515" duration="240"/>
   <frame tileid="510" duration="240"/>
   <frame tileid="505" duration="240"/>
  </animation>
 </tile>
 <tile id="501" terrain="5,5,1,1">
  <properties>
   <property name="type" value="shore"/>
  </properties>
  <animation>
   <frame tileid="501" duration="240"/>
   <frame tileid="506" duration="240"/>
   <frame tileid="511" duration="240"/>
   <frame tileid="516" duration="240"/>
   <frame tileid="511" duration="240"/>
   <frame tileid="506" duration="240"/>
  </animation>
 </tile>
 <tile id="502" terrain="5,1,1,1">
  <properties>
   <property name="type" value="shore_walkable"/>
  </properties>
  <animation>
   <frame tileid="502" duration="240"/>
   <frame tileid="507" duration="240"/>
   <frame tileid="512" duration="240"/>
   <frame tileid="517" duration="240"/>
   <frame tileid="512" duration="240"/>
   <frame tileid="507" duration="240"/>
  </animation>
 </tile>
 <tile id="503" terrain="1,5,5,1">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="503" duration="240"/>
   <frame tileid="508" duration="240"/>
   <frame tileid="513" duration="240"/>
   <frame tileid="518" duration="240"/>
   <frame tileid="513" duration="240"/>
   <frame tileid="508" duration="240"/>
  </animation>
 </tile>
 <tile id="504" terrain="5,1,1,5">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="504" duration="240"/>
   <frame tileid="509" duration="240"/>
   <frame tileid="514" duration="240"/>
   <frame tileid="519" duration="240"/>
   <frame tileid="514" duration="240"/>
   <frame tileid="509" duration="240"/>
  </animation>
 </tile>
 <tile id="505">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="506">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="507">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="508">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="509">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="510">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="511">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="512">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="513">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="514">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="515">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="516">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="517">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="518">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="519">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="520" terrain="6,6,6,4">
  <properties>
   <property name="type" value="cliff"/>
  </properties>
 </tile>
 <tile id="521" terrain="6,6,4,4">
  <properties>
   <property name="type" value="cliff"/>
  </properties>
 </tile>
 <tile id="522" terrain="6,6,4,6">
  <properties>
   <property name="type" value="cliff"/>
  </properties>
 </tile>
 <tile id="523" terrain="6,4,4,4">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="524" terrain="4,6,4,4">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="525">
  <properties>
   <property name="type" value="cliff"/>
  </properties>
 </tile>
 <tile id="526">
  <properties>
   <property name="type" value="cliff"/>
  </properties>
 </tile>
 <tile id="527">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="528">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="529">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="530">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="531">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="532">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="533">
  <properties>
   <property name="type" value="walls"/>
  </properties>
 </tile>
 <tile id="534">
  <properties>
   <property name="type" value="walls"/>
  </properties>
 </tile>
 <tile id="535">
  <properties>
   <property name="type" value="walls"/>
  </properties>
 </tile>
 <tile id="536">
  <properties>
   <property name="type" value="walls"/>
  </properties>
 </tile>
 <tile id="537">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="538">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="539">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="540" terrain="4,4,4,5">
  <properties>
   <property name="type" value="shore_cliff"/>
  </properties>
  <animation>
   <frame tileid="540" duration="240"/>
   <frame tileid="545" duration="240"/>
   <frame tileid="550" duration="240"/>
   <frame tileid="555" duration="240"/>
   <frame tileid="550" duration="240"/>
   <frame tileid="545" duration="240"/>
  </animation>
 </tile>
 <tile id="541" terrain="4,4,5,5">
  <properties>
   <property name="type" value="shore_cliff"/>
  </properties>
  <animation>
   <frame tileid="541" duration="240"/>
   <frame tileid="546" duration="240"/>
   <frame tileid="551" duration="240"/>
   <frame tileid="556" duration="240"/>
   <frame tileid="551" duration="240"/>
   <frame tileid="546" duration="240"/>
  </animation>
 </tile>
 <tile id="542" terrain="4,4,5,4">
  <properties>
   <property name="type" value="shore_cliff"/>
  </properties>
  <animation>
   <frame tileid="542" duration="240"/>
   <frame tileid="547" duration="240"/>
   <frame tileid="552" duration="240"/>
   <frame tileid="557" duration="240"/>
   <frame tileid="552" duration="240"/>
   <frame tileid="547" duration="240"/>
  </animation>
 </tile>
 <tile id="543" terrain="4,5,5,5">
  <properties>
   <property name="type" value="shore_cliff"/>
  </properties>
  <animation>
   <frame tileid="543" duration="240"/>
   <frame tileid="548" duration="240"/>
   <frame tileid="553" duration="240"/>
   <frame tileid="558" duration="240"/>
   <frame tileid="553" duration="240"/>
   <frame tileid="548" duration="240"/>
  </animation>
 </tile>
 <tile id="544" terrain="5,4,5,5">
  <properties>
   <property name="type" value="shore_cliff"/>
  </properties>
  <animation>
   <frame tileid="544" duration="240"/>
   <frame tileid="549" duration="240"/>
   <frame tileid="554" duration="240"/>
   <frame tileid="559" duration="240"/>
   <frame tileid="554" duration="240"/>
   <frame tileid="549" duration="240"/>
  </animation>
 </tile>
 <tile id="545">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="546">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="547">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="548">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="549">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="550">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="551">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="552">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="553">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="554">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="555">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="556">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="557">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="558">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="559">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="560" terrain="6,4,6,4">
  <properties>
   <property name="type" value="cliff"/>
  </properties>
 </tile>
 <tile id="561" terrain="4,4,4,4">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="562" terrain="4,6,4,6">
  <properties>
   <property name="type" value="cliff"/>
  </properties>
 </tile>
 <tile id="563" terrain="4,4,6,4">
  <properties>
   <property name="type" value="cliff"/>
  </properties>
 </tile>
 <tile id="564" terrain="4,4,4,6">
  <properties>
   <property name="type" value="cliff"/>
  </properties>
 </tile>
 <tile id="565">
  <properties>
   <property name="type" value="cliff"/>
  </properties>
 </tile>
 <tile id="566">
  <properties>
   <property name="type" value="cliff"/>
  </properties>
 </tile>
 <tile id="567">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="568">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="569">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="570">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="571">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="572">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="573">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="574">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="575">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="576">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="577">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="578">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="579">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="580" terrain="4,5,4,5">
  <properties>
   <property name="type" value="shore_cliff"/>
  </properties>
  <animation>
   <frame tileid="580" duration="240"/>
   <frame tileid="585" duration="240"/>
   <frame tileid="590" duration="240"/>
   <frame tileid="595" duration="240"/>
   <frame tileid="590" duration="240"/>
   <frame tileid="585" duration="240"/>
  </animation>
 </tile>
 <tile id="581" terrain="5,5,5,5" probability="0">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="582" terrain="5,4,5,4">
  <properties>
   <property name="type" value="shore_cliff"/>
  </properties>
  <animation>
   <frame tileid="582" duration="240"/>
   <frame tileid="587" duration="240"/>
   <frame tileid="592" duration="240"/>
   <frame tileid="597" duration="240"/>
   <frame tileid="592" duration="240"/>
   <frame tileid="587" duration="240"/>
  </animation>
 </tile>
 <tile id="583" terrain="5,5,4,5">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="583" duration="240"/>
   <frame tileid="588" duration="240"/>
   <frame tileid="593" duration="240"/>
   <frame tileid="598" duration="240"/>
   <frame tileid="593" duration="240"/>
   <frame tileid="588" duration="240"/>
  </animation>
 </tile>
 <tile id="584" terrain="5,5,5,4">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="584" duration="240"/>
   <frame tileid="589" duration="240"/>
   <frame tileid="594" duration="240"/>
   <frame tileid="599" duration="240"/>
   <frame tileid="594" duration="240"/>
   <frame tileid="589" duration="240"/>
  </animation>
 </tile>
 <tile id="585">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="586">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="587">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="588">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="589">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="590">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="591">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="592">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="593">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="594">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="595">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="596">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="597">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="598">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="599">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="600" terrain="6,4,6,6">
  <properties>
   <property name="type" value="cliff"/>
  </properties>
 </tile>
 <tile id="601" terrain="4,4,6,6">
  <properties>
   <property name="type" value="cliff"/>
  </properties>
 </tile>
 <tile id="602" terrain="4,6,6,6">
  <properties>
   <property name="type" value="cliff"/>
  </properties>
 </tile>
 <tile id="603" terrain="6,4,4,6">
  <properties>
   <property name="type" value="cliff"/>
  </properties>
 </tile>
 <tile id="604" terrain="4,6,6,4">
  <properties>
   <property name="type" value="cliff"/>
  </properties>
 </tile>
 <tile id="605">
  <properties>
   <property name="type" value="cliff"/>
  </properties>
 </tile>
 <tile id="606">
  <properties>
   <property name="type" value="cliff"/>
  </properties>
 </tile>
 <tile id="607">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="608">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="609">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="610">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="611">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="612">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="613">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="614">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="615">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="616">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="617">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="618">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="619">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="620" terrain="4,5,4,4">
  <properties>
   <property name="type" value="shore_cliff_walkable"/>
  </properties>
  <animation>
   <frame tileid="620" duration="240"/>
   <frame tileid="625" duration="240"/>
   <frame tileid="630" duration="240"/>
   <frame tileid="635" duration="240"/>
   <frame tileid="630" duration="240"/>
   <frame tileid="625" duration="240"/>
  </animation>
 </tile>
 <tile id="621" terrain="5,5,4,4">
  <properties>
   <property name="type" value="shore_cliff"/>
  </properties>
  <animation>
   <frame tileid="621" duration="240"/>
   <frame tileid="626" duration="240"/>
   <frame tileid="631" duration="240"/>
   <frame tileid="636" duration="240"/>
   <frame tileid="631" duration="240"/>
   <frame tileid="626" duration="240"/>
  </animation>
 </tile>
 <tile id="622" terrain="5,4,4,4">
  <properties>
   <property name="type" value="shore_cliff_walkable"/>
  </properties>
  <animation>
   <frame tileid="622" duration="240"/>
   <frame tileid="627" duration="240"/>
   <frame tileid="632" duration="240"/>
   <frame tileid="637" duration="240"/>
   <frame tileid="632" duration="240"/>
   <frame tileid="627" duration="240"/>
  </animation>
 </tile>
 <tile id="623" terrain="4,5,5,4">
  <properties>
   <property name="type" value="shore_cliff"/>
  </properties>
  <animation>
   <frame tileid="623" duration="240"/>
   <frame tileid="628" duration="240"/>
   <frame tileid="633" duration="240"/>
   <frame tileid="638" duration="240"/>
   <frame tileid="633" duration="240"/>
   <frame tileid="628" duration="240"/>
  </animation>
 </tile>
 <tile id="624" terrain="5,4,4,5">
  <properties>
   <property name="type" value="shore_cliff"/>
  </properties>
  <animation>
   <frame tileid="624" duration="240"/>
   <frame tileid="629" duration="240"/>
   <frame tileid="634" duration="240"/>
   <frame tileid="639" duration="240"/>
   <frame tileid="634" duration="240"/>
   <frame tileid="629" duration="240"/>
  </animation>
 </tile>
 <tile id="625">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="626">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="627">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="628">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="629">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="630">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="631">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="632">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="633">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="634">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="635">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="636">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="637">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="638">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="639">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="640" terrain="1,1,1,6">
  <properties>
   <property name="type" value="desert"/>
  </properties>
 </tile>
 <tile id="641" terrain="1,1,6,6">
  <properties>
   <property name="type" value="desert"/>
  </properties>
 </tile>
 <tile id="642" terrain="1,1,6,1">
  <properties>
   <property name="type" value="desert"/>
  </properties>
 </tile>
 <tile id="643" terrain="1,1,1,6">
  <properties>
   <property name="type" value="desert"/>
  </properties>
 </tile>
 <tile id="644" terrain="1,1,6,1">
  <properties>
   <property name="type" value="desert"/>
  </properties>
 </tile>
 <tile id="645">
  <properties>
   <property name="type" value="cliff"/>
  </properties>
 </tile>
 <tile id="646">
  <properties>
   <property name="type" value="cliff"/>
  </properties>
 </tile>
 <tile id="647">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="648">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="649">
  <properties>
   <property name="type" value="cliff"/>
  </properties>
 </tile>
 <tile id="650">
  <properties>
   <property name="type" value="cliff"/>
  </properties>
 </tile>
 <tile id="651">
  <properties>
   <property name="type" value="cliff"/>
  </properties>
 </tile>
 <tile id="652" terrain=",,,11">
  <properties>
   <property name="type" value="pine_forest"/>
  </properties>
 </tile>
 <tile id="653" terrain=",,11,11">
  <properties>
   <property name="type" value="pine_forest"/>
  </properties>
 </tile>
 <tile id="654" terrain=",,11,">
  <properties>
   <property name="type" value="pine_forest"/>
  </properties>
 </tile>
 <tile id="655" terrain=",11,11,11">
  <properties>
   <property name="type" value="pine_forest"/>
  </properties>
 </tile>
 <tile id="656" terrain="11,,11,11">
  <properties>
   <property name="type" value="pine_forest"/>
  </properties>
 </tile>
 <tile id="657" terrain="11,11,11,11">
  <properties>
   <property name="type" value="pine_forest"/>
  </properties>
 </tile>
 <tile id="658">
  <properties>
   <property name="type" value="pine_forest"/>
  </properties>
 </tile>
 <tile id="659">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="660" terrain="6,6,6,5">
  <properties>
   <property name="type" value="beach"/>
  </properties>
  <animation>
   <frame tileid="660" duration="240"/>
   <frame tileid="665" duration="240"/>
   <frame tileid="670" duration="240"/>
   <frame tileid="675" duration="240"/>
   <frame tileid="670" duration="240"/>
   <frame tileid="665" duration="240"/>
  </animation>
 </tile>
 <tile id="661" terrain="6,6,5,5">
  <properties>
   <property name="type" value="beach"/>
  </properties>
  <animation>
   <frame tileid="661" duration="240"/>
   <frame tileid="666" duration="240"/>
   <frame tileid="671" duration="240"/>
   <frame tileid="676" duration="240"/>
   <frame tileid="671" duration="240"/>
   <frame tileid="666" duration="240"/>
  </animation>
 </tile>
 <tile id="662" terrain="6,6,5,6">
  <properties>
   <property name="type" value="beach"/>
  </properties>
  <animation>
   <frame tileid="662" duration="240"/>
   <frame tileid="667" duration="240"/>
   <frame tileid="672" duration="240"/>
   <frame tileid="677" duration="240"/>
   <frame tileid="672" duration="240"/>
   <frame tileid="667" duration="240"/>
  </animation>
 </tile>
 <tile id="663" terrain="6,5,5,5">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="663" duration="240"/>
   <frame tileid="668" duration="240"/>
   <frame tileid="673" duration="240"/>
   <frame tileid="678" duration="240"/>
   <frame tileid="673" duration="240"/>
   <frame tileid="668" duration="240"/>
  </animation>
 </tile>
 <tile id="664" terrain="5,6,5,5">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="664" duration="240"/>
   <frame tileid="669" duration="240"/>
   <frame tileid="674" duration="240"/>
   <frame tileid="679" duration="240"/>
   <frame tileid="674" duration="240"/>
   <frame tileid="669" duration="240"/>
  </animation>
 </tile>
 <tile id="665">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="666">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="667">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="668">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="669">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="670">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="671">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="672">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="673">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="674">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="675">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="676">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="677">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="678">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="679">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="680" terrain="1,6,1,6">
  <properties>
   <property name="type" value="desert"/>
  </properties>
 </tile>
 <tile id="681" terrain="6,6,6,6">
  <properties>
   <property name="type" value="desert"/>
  </properties>
 </tile>
 <tile id="682" terrain="6,1,6,1">
  <properties>
   <property name="type" value="desert"/>
  </properties>
 </tile>
 <tile id="683" terrain="1,6,1,1">
  <properties>
   <property name="type" value="desert"/>
  </properties>
 </tile>
 <tile id="684" terrain="6,1,1,1">
  <properties>
   <property name="type" value="desert"/>
  </properties>
 </tile>
 <tile id="685" terrain="4,1,4,6">
  <properties>
   <property name="type" value="cliff"/>
  </properties>
 </tile>
 <tile id="686" terrain="1,4,6,4">
  <properties>
   <property name="type" value="cliff"/>
  </properties>
 </tile>
 <tile id="687" terrain="4,4,1,6">
  <properties>
   <property name="type" value="cliff"/>
  </properties>
 </tile>
 <tile id="688" terrain="4,4,6,1">
  <properties>
   <property name="type" value="cliff"/>
  </properties>
 </tile>
 <tile id="689">
  <properties>
   <property name="type" value="cliff"/>
  </properties>
 </tile>
 <tile id="690">
  <properties>
   <property name="type" value="cliff"/>
  </properties>
 </tile>
 <tile id="691">
  <properties>
   <property name="type" value="cliff"/>
  </properties>
 </tile>
 <tile id="692" terrain=",11,,11">
  <properties>
   <property name="type" value="pine_forest"/>
  </properties>
 </tile>
 <tile id="693" terrain="11,11,11,11">
  <properties>
   <property name="type" value="pine_forest"/>
  </properties>
 </tile>
 <tile id="694" terrain="11,,11,">
  <properties>
   <property name="type" value="pine_forest"/>
  </properties>
 </tile>
 <tile id="695" terrain="11,11,,11">
  <properties>
   <property name="type" value="pine_forest"/>
  </properties>
 </tile>
 <tile id="696" terrain="11,11,11,">
  <properties>
   <property name="type" value="pine_forest"/>
  </properties>
 </tile>
 <tile id="697" terrain="11,11,11,11">
  <properties>
   <property name="type" value="pine_forest"/>
  </properties>
 </tile>
 <tile id="698">
  <properties>
   <property name="type" value="pine_forest"/>
  </properties>
 </tile>
 <tile id="699">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="700" terrain="6,5,6,5">
  <properties>
   <property name="type" value="beach"/>
  </properties>
  <animation>
   <frame tileid="700" duration="240"/>
   <frame tileid="705" duration="240"/>
   <frame tileid="710" duration="240"/>
   <frame tileid="715" duration="240"/>
   <frame tileid="710" duration="240"/>
   <frame tileid="705" duration="240"/>
  </animation>
 </tile>
 <tile id="701" terrain="5,5,5,5">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="702" terrain="5,6,5,6">
  <properties>
   <property name="type" value="beach"/>
  </properties>
  <animation>
   <frame tileid="702" duration="240"/>
   <frame tileid="707" duration="240"/>
   <frame tileid="712" duration="240"/>
   <frame tileid="717" duration="240"/>
   <frame tileid="712" duration="240"/>
   <frame tileid="707" duration="240"/>
  </animation>
 </tile>
 <tile id="703" terrain="5,5,6,5">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="703" duration="240"/>
   <frame tileid="708" duration="240"/>
   <frame tileid="713" duration="240"/>
   <frame tileid="718" duration="240"/>
   <frame tileid="713" duration="240"/>
   <frame tileid="708" duration="240"/>
  </animation>
 </tile>
 <tile id="704" terrain="5,5,5,6">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="704" duration="240"/>
   <frame tileid="709" duration="240"/>
   <frame tileid="714" duration="240"/>
   <frame tileid="719" duration="240"/>
   <frame tileid="714" duration="240"/>
   <frame tileid="709" duration="240"/>
  </animation>
 </tile>
 <tile id="705">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="706">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="707">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="708">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="709">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="710">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="711">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="712">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="713">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="714">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="715">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="716">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="717">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="718">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="719">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="720" terrain="1,6,1,1">
  <properties>
   <property name="type" value="desert"/>
  </properties>
 </tile>
 <tile id="721" terrain="6,6,1,1">
  <properties>
   <property name="type" value="desert"/>
  </properties>
 </tile>
 <tile id="722" terrain="6,1,1,1">
  <properties>
   <property name="type" value="desert"/>
  </properties>
 </tile>
 <tile id="723">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="724">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="725" terrain="4,6,4,1">
  <properties>
   <property name="type" value="cliff"/>
  </properties>
 </tile>
 <tile id="726" terrain="6,4,1,4">
  <properties>
   <property name="type" value="cliff"/>
  </properties>
 </tile>
 <tile id="727" terrain="1,6,4,4">
  <properties>
   <property name="type" value="cliff"/>
  </properties>
 </tile>
 <tile id="728" terrain="6,1,4,4">
  <properties>
   <property name="type" value="cliff"/>
  </properties>
 </tile>
 <tile id="729">
  <properties>
   <property name="type" value="cliff"/>
  </properties>
 </tile>
 <tile id="730">
  <properties>
   <property name="type" value="cliff"/>
  </properties>
 </tile>
 <tile id="731">
  <properties>
   <property name="type" value="cliff"/>
  </properties>
 </tile>
 <tile id="732" terrain=",11,,">
  <properties>
   <property name="type" value="pine_forest"/>
  </properties>
 </tile>
 <tile id="733" terrain="11,11,,">
  <properties>
   <property name="type" value="pine_forest"/>
  </properties>
 </tile>
 <tile id="734" terrain="11,,,">
  <properties>
   <property name="type" value="pine_forest"/>
  </properties>
 </tile>
 <tile id="735" terrain=",11,11,">
  <properties>
   <property name="type" value="pine_forest"/>
  </properties>
 </tile>
 <tile id="736" terrain="11,,,11">
  <properties>
   <property name="type" value="pine_forest"/>
  </properties>
 </tile>
 <tile id="737" terrain="11,11,11,11">
  <properties>
   <property name="type" value="pine_forest"/>
  </properties>
 </tile>
 <tile id="738">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="739">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="740" terrain="6,5,6,6">
  <properties>
   <property name="type" value="beach_walkable"/>
  </properties>
  <animation>
   <frame tileid="740" duration="240"/>
   <frame tileid="745" duration="240"/>
   <frame tileid="750" duration="240"/>
   <frame tileid="755" duration="240"/>
   <frame tileid="750" duration="240"/>
   <frame tileid="745" duration="240"/>
  </animation>
 </tile>
 <tile id="741" terrain="5,5,6,6">
  <properties>
   <property name="type" value="beach"/>
  </properties>
  <animation>
   <frame tileid="741" duration="240"/>
   <frame tileid="746" duration="240"/>
   <frame tileid="751" duration="240"/>
   <frame tileid="756" duration="240"/>
   <frame tileid="751" duration="240"/>
   <frame tileid="746" duration="240"/>
  </animation>
 </tile>
 <tile id="742" terrain="5,6,6,6">
  <properties>
   <property name="type" value="beach_walkable"/>
  </properties>
  <animation>
   <frame tileid="742" duration="240"/>
   <frame tileid="747" duration="240"/>
   <frame tileid="752" duration="240"/>
   <frame tileid="757" duration="240"/>
   <frame tileid="752" duration="240"/>
   <frame tileid="747" duration="240"/>
  </animation>
 </tile>
 <tile id="743" terrain="6,5,5,6">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="743" duration="240"/>
   <frame tileid="748" duration="240"/>
   <frame tileid="753" duration="240"/>
   <frame tileid="758" duration="240"/>
   <frame tileid="753" duration="240"/>
   <frame tileid="748" duration="240"/>
  </animation>
 </tile>
 <tile id="744" terrain="5,6,6,5">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="744" duration="240"/>
   <frame tileid="749" duration="240"/>
   <frame tileid="754" duration="240"/>
   <frame tileid="759" duration="240"/>
   <frame tileid="754" duration="240"/>
   <frame tileid="749" duration="240"/>
  </animation>
 </tile>
 <tile id="745">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="746">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="747">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="748">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="749">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="750">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="751">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="752">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="753">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="754">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="755">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="756">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="757">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="758">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="759">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="760" terrain="9,9,9,8">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="760" duration="240"/>
   <frame tileid="765" duration="240"/>
   <frame tileid="770" duration="240"/>
   <frame tileid="775" duration="240"/>
   <frame tileid="770" duration="240"/>
   <frame tileid="765" duration="240"/>
  </animation>
 </tile>
 <tile id="761" terrain="9,9,8,8">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="761" duration="240"/>
   <frame tileid="766" duration="240"/>
   <frame tileid="771" duration="240"/>
   <frame tileid="776" duration="240"/>
   <frame tileid="771" duration="240"/>
   <frame tileid="766" duration="240"/>
  </animation>
 </tile>
 <tile id="762" terrain="9,9,8,9">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="762" duration="240"/>
   <frame tileid="767" duration="240"/>
   <frame tileid="772" duration="240"/>
   <frame tileid="777" duration="240"/>
   <frame tileid="772" duration="240"/>
   <frame tileid="767" duration="240"/>
  </animation>
 </tile>
 <tile id="763" terrain="9,8,8,8">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="763" duration="240"/>
   <frame tileid="768" duration="240"/>
   <frame tileid="773" duration="240"/>
   <frame tileid="778" duration="240"/>
   <frame tileid="773" duration="240"/>
   <frame tileid="768" duration="240"/>
  </animation>
 </tile>
 <tile id="764" terrain="8,9,8,8">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="764" duration="240"/>
   <frame tileid="769" duration="240"/>
   <frame tileid="774" duration="240"/>
   <frame tileid="779" duration="240"/>
   <frame tileid="774" duration="240"/>
   <frame tileid="769" duration="240"/>
  </animation>
 </tile>
 <tile id="765">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="766">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="767">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="768">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="769">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="770">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="771">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="772">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="773">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="774">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="775">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="776">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="777">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="778">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="779">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="780" terrain="8,8,8,7">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="780" duration="240"/>
   <frame tileid="785" duration="240"/>
   <frame tileid="790" duration="240"/>
   <frame tileid="795" duration="240"/>
   <frame tileid="790" duration="240"/>
   <frame tileid="785" duration="240"/>
  </animation>
 </tile>
 <tile id="781" terrain="8,8,7,7">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="781" duration="240"/>
   <frame tileid="786" duration="240"/>
   <frame tileid="791" duration="240"/>
   <frame tileid="796" duration="240"/>
   <frame tileid="791" duration="240"/>
   <frame tileid="786" duration="240"/>
  </animation>
 </tile>
 <tile id="782" terrain="8,8,7,8">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="782" duration="240"/>
   <frame tileid="787" duration="240"/>
   <frame tileid="792" duration="240"/>
   <frame tileid="797" duration="240"/>
   <frame tileid="792" duration="240"/>
   <frame tileid="787" duration="240"/>
  </animation>
 </tile>
 <tile id="783" terrain="8,7,7,7">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="783" duration="240"/>
   <frame tileid="788" duration="240"/>
   <frame tileid="793" duration="240"/>
   <frame tileid="798" duration="240"/>
   <frame tileid="793" duration="240"/>
   <frame tileid="788" duration="240"/>
  </animation>
 </tile>
 <tile id="784" terrain="7,8,7,7">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="784" duration="240"/>
   <frame tileid="789" duration="240"/>
   <frame tileid="794" duration="240"/>
   <frame tileid="799" duration="240"/>
   <frame tileid="794" duration="240"/>
   <frame tileid="789" duration="240"/>
  </animation>
 </tile>
 <tile id="785">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="786">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="787">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="788">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="789">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="790">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="791">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="792">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="793">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="794">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="795">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="796">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="797">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="798">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="799">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="800" terrain="9,8,9,8">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="800" duration="240"/>
   <frame tileid="805" duration="240"/>
   <frame tileid="810" duration="240"/>
   <frame tileid="815" duration="240"/>
   <frame tileid="810" duration="240"/>
   <frame tileid="805" duration="240"/>
  </animation>
 </tile>
 <tile id="801" terrain="8,8,8,8">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="802" terrain="8,9,8,9">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="802" duration="240"/>
   <frame tileid="807" duration="240"/>
   <frame tileid="812" duration="240"/>
   <frame tileid="817" duration="240"/>
   <frame tileid="812" duration="240"/>
   <frame tileid="807" duration="240"/>
  </animation>
 </tile>
 <tile id="803" terrain="8,8,9,8">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="803" duration="240"/>
   <frame tileid="808" duration="240"/>
   <frame tileid="813" duration="240"/>
   <frame tileid="818" duration="240"/>
   <frame tileid="813" duration="240"/>
   <frame tileid="808" duration="240"/>
  </animation>
 </tile>
 <tile id="804" terrain="8,8,8,9">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="804" duration="240"/>
   <frame tileid="809" duration="240"/>
   <frame tileid="814" duration="240"/>
   <frame tileid="819" duration="240"/>
   <frame tileid="814" duration="240"/>
   <frame tileid="809" duration="240"/>
  </animation>
 </tile>
 <tile id="805">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="806">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="807">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="808">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="809">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="810">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="811">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="812">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="813">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="814">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="815">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="816">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="817">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="818">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="819">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="820" terrain="8,7,8,7">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="820" duration="240"/>
   <frame tileid="825" duration="240"/>
   <frame tileid="830" duration="240"/>
   <frame tileid="835" duration="240"/>
   <frame tileid="830" duration="240"/>
   <frame tileid="825" duration="240"/>
  </animation>
 </tile>
 <tile id="821" terrain="7,7,7,7">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="822" terrain="7,8,7,8">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="822" duration="240"/>
   <frame tileid="827" duration="240"/>
   <frame tileid="832" duration="240"/>
   <frame tileid="837" duration="240"/>
   <frame tileid="832" duration="240"/>
   <frame tileid="827" duration="240"/>
  </animation>
 </tile>
 <tile id="823" terrain="7,7,8,7">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="823" duration="240"/>
   <frame tileid="828" duration="240"/>
   <frame tileid="833" duration="240"/>
   <frame tileid="838" duration="240"/>
   <frame tileid="833" duration="240"/>
   <frame tileid="828" duration="240"/>
  </animation>
 </tile>
 <tile id="824" terrain="7,7,7,8">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="824" duration="240"/>
   <frame tileid="829" duration="240"/>
   <frame tileid="834" duration="240"/>
   <frame tileid="839" duration="240"/>
   <frame tileid="834" duration="240"/>
   <frame tileid="829" duration="240"/>
  </animation>
 </tile>
 <tile id="825">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="826">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="827">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="828">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="829">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="830">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="831">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="832">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="833">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="834">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="835">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="836">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="837">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="838">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="839">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="840" terrain="9,8,9,9">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="840" duration="240"/>
   <frame tileid="845" duration="240"/>
   <frame tileid="850" duration="240"/>
   <frame tileid="855" duration="240"/>
   <frame tileid="850" duration="240"/>
   <frame tileid="845" duration="240"/>
  </animation>
 </tile>
 <tile id="841" terrain="8,8,9,9">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="841" duration="240"/>
   <frame tileid="846" duration="240"/>
   <frame tileid="851" duration="240"/>
   <frame tileid="856" duration="240"/>
   <frame tileid="851" duration="240"/>
   <frame tileid="846" duration="240"/>
  </animation>
 </tile>
 <tile id="842" terrain="8,9,9,9">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="842" duration="240"/>
   <frame tileid="847" duration="240"/>
   <frame tileid="852" duration="240"/>
   <frame tileid="857" duration="240"/>
   <frame tileid="852" duration="240"/>
   <frame tileid="847" duration="240"/>
  </animation>
 </tile>
 <tile id="843" terrain="9,8,8,9">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="843" duration="240"/>
   <frame tileid="848" duration="240"/>
   <frame tileid="853" duration="240"/>
   <frame tileid="858" duration="240"/>
   <frame tileid="853" duration="240"/>
   <frame tileid="848" duration="240"/>
  </animation>
 </tile>
 <tile id="844" terrain="8,9,9,8">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="844" duration="240"/>
   <frame tileid="849" duration="240"/>
   <frame tileid="854" duration="240"/>
   <frame tileid="859" duration="240"/>
   <frame tileid="854" duration="240"/>
   <frame tileid="849" duration="240"/>
  </animation>
 </tile>
 <tile id="845">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="846">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="847">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="848">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="849">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="850">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="851">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="852">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="853">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="854">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="855">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="856">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="857">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="858">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="859">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="860" terrain="8,7,8,8">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="860" duration="240"/>
   <frame tileid="865" duration="240"/>
   <frame tileid="870" duration="240"/>
   <frame tileid="875" duration="240"/>
   <frame tileid="870" duration="240"/>
   <frame tileid="865" duration="240"/>
  </animation>
 </tile>
 <tile id="861" terrain="7,7,8,8">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="861" duration="240"/>
   <frame tileid="866" duration="240"/>
   <frame tileid="871" duration="240"/>
   <frame tileid="876" duration="240"/>
   <frame tileid="871" duration="240"/>
   <frame tileid="866" duration="240"/>
  </animation>
 </tile>
 <tile id="862" terrain="7,8,8,8">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="862" duration="240"/>
   <frame tileid="867" duration="240"/>
   <frame tileid="872" duration="240"/>
   <frame tileid="877" duration="240"/>
   <frame tileid="872" duration="240"/>
   <frame tileid="867" duration="240"/>
  </animation>
 </tile>
 <tile id="863" terrain="8,7,7,8">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="863" duration="240"/>
   <frame tileid="868" duration="240"/>
   <frame tileid="873" duration="240"/>
   <frame tileid="878" duration="240"/>
   <frame tileid="873" duration="240"/>
   <frame tileid="868" duration="240"/>
  </animation>
 </tile>
 <tile id="864" terrain="7,8,8,7">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="864" duration="240"/>
   <frame tileid="869" duration="240"/>
   <frame tileid="874" duration="240"/>
   <frame tileid="879" duration="240"/>
   <frame tileid="874" duration="240"/>
   <frame tileid="869" duration="240"/>
  </animation>
 </tile>
 <tile id="865">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="866">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="867">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="868">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="869">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="870">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="871">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="872">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="873">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="874">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="875">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="876">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="877">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="878">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="879">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="880">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="880" duration="240"/>
   <frame tileid="884" duration="240"/>
   <frame tileid="888" duration="240"/>
   <frame tileid="892" duration="240"/>
   <frame tileid="888" duration="240"/>
   <frame tileid="884" duration="240"/>
  </animation>
 </tile>
 <tile id="881">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="881" duration="240"/>
   <frame tileid="885" duration="240"/>
   <frame tileid="889" duration="240"/>
   <frame tileid="893" duration="240"/>
   <frame tileid="889" duration="240"/>
   <frame tileid="885" duration="240"/>
  </animation>
 </tile>
 <tile id="882">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="882" duration="240"/>
   <frame tileid="886" duration="240"/>
   <frame tileid="890" duration="240"/>
   <frame tileid="894" duration="240"/>
   <frame tileid="890" duration="240"/>
   <frame tileid="886" duration="240"/>
  </animation>
 </tile>
 <tile id="883">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="883" duration="240"/>
   <frame tileid="887" duration="240"/>
   <frame tileid="891" duration="240"/>
   <frame tileid="895" duration="240"/>
   <frame tileid="891" duration="240"/>
   <frame tileid="887" duration="240"/>
  </animation>
 </tile>
 <tile id="884">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="885">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="886">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="887">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="888">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="889">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="890">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="891">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="892">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="893">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="894">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="895">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="896" terrain="9,9,9,9">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="897" terrain="10,10,10,10">
  <properties>
   <property name="type" value="swamp"/>
  </properties>
 </tile>
 <tile id="898" terrain="10,10,10,10">
  <properties>
   <property name="type" value="swamp"/>
  </properties>
 </tile>
 <tile id="899" terrain="10,10,10,10">
  <properties>
   <property name="type" value="swamp"/>
  </properties>
 </tile>
 <tile id="900">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="900" duration="240"/>
   <frame tileid="904" duration="240"/>
   <frame tileid="908" duration="240"/>
   <frame tileid="912" duration="240"/>
   <frame tileid="908" duration="240"/>
   <frame tileid="904" duration="240"/>
  </animation>
 </tile>
 <tile id="901">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="901" duration="240"/>
   <frame tileid="905" duration="240"/>
   <frame tileid="909" duration="240"/>
   <frame tileid="913" duration="240"/>
   <frame tileid="909" duration="240"/>
   <frame tileid="905" duration="240"/>
  </animation>
 </tile>
 <tile id="902">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="902" duration="240"/>
   <frame tileid="906" duration="240"/>
   <frame tileid="910" duration="240"/>
   <frame tileid="914" duration="240"/>
   <frame tileid="910" duration="240"/>
   <frame tileid="906" duration="240"/>
  </animation>
 </tile>
 <tile id="903">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="903" duration="240"/>
   <frame tileid="907" duration="240"/>
   <frame tileid="911" duration="240"/>
   <frame tileid="915" duration="240"/>
   <frame tileid="911" duration="240"/>
   <frame tileid="907" duration="240"/>
  </animation>
 </tile>
 <tile id="904">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="905">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="906">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="907">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="908">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="909">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="910">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="911">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="912">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="913">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="914">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="915">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="916">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="917">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="918">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="919">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="920">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="920" duration="240"/>
   <frame tileid="924" duration="240"/>
   <frame tileid="928" duration="240"/>
   <frame tileid="932" duration="240"/>
   <frame tileid="928" duration="240"/>
   <frame tileid="924" duration="240"/>
  </animation>
 </tile>
 <tile id="921">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="921" duration="240"/>
   <frame tileid="925" duration="240"/>
   <frame tileid="929" duration="240"/>
   <frame tileid="933" duration="240"/>
   <frame tileid="929" duration="240"/>
   <frame tileid="925" duration="240"/>
  </animation>
 </tile>
 <tile id="922">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="922" duration="240"/>
   <frame tileid="926" duration="240"/>
   <frame tileid="930" duration="240"/>
   <frame tileid="934" duration="240"/>
   <frame tileid="930" duration="240"/>
   <frame tileid="926" duration="240"/>
  </animation>
 </tile>
 <tile id="923">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="923" duration="240"/>
   <frame tileid="927" duration="240"/>
   <frame tileid="931" duration="240"/>
   <frame tileid="935" duration="240"/>
   <frame tileid="931" duration="240"/>
   <frame tileid="927" duration="240"/>
  </animation>
 </tile>
 <tile id="924">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="925">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="926">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="927">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="928">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="929">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="930">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="931">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="932">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="933">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="934">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="935">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="936" terrain="1,1,1,10">
  <properties>
   <property name="type" value="swamp"/>
  </properties>
 </tile>
 <tile id="937" terrain="1,1,10,10">
  <properties>
   <property name="type" value="swamp"/>
  </properties>
 </tile>
 <tile id="938" terrain="1,1,10,1">
  <properties>
   <property name="type" value="swamp"/>
  </properties>
 </tile>
 <tile id="939" terrain="10,10,10,10">
  <properties>
   <property name="type" value="swamp"/>
  </properties>
 </tile>
 <tile id="940">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="940" duration="240"/>
   <frame tileid="944" duration="240"/>
   <frame tileid="948" duration="240"/>
   <frame tileid="952" duration="240"/>
   <frame tileid="948" duration="240"/>
   <frame tileid="944" duration="240"/>
  </animation>
 </tile>
 <tile id="941">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="941" duration="240"/>
   <frame tileid="945" duration="240"/>
   <frame tileid="949" duration="240"/>
   <frame tileid="953" duration="240"/>
   <frame tileid="949" duration="240"/>
   <frame tileid="945" duration="240"/>
  </animation>
 </tile>
 <tile id="942">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="942" duration="240"/>
   <frame tileid="946" duration="240"/>
   <frame tileid="950" duration="240"/>
   <frame tileid="954" duration="240"/>
   <frame tileid="950" duration="240"/>
   <frame tileid="946" duration="240"/>
  </animation>
 </tile>
 <tile id="943">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="943" duration="240"/>
   <frame tileid="947" duration="240"/>
   <frame tileid="951" duration="240"/>
   <frame tileid="955" duration="240"/>
   <frame tileid="951" duration="240"/>
   <frame tileid="947" duration="240"/>
  </animation>
 </tile>
 <tile id="944">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="945">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="946">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="947">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="948">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="949">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="950">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="951">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="952">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="953">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="954">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="955">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="956">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="957">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="958">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="959">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="960">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="960" duration="240"/>
   <frame tileid="964" duration="240"/>
   <frame tileid="968" duration="240"/>
   <frame tileid="972" duration="240"/>
   <frame tileid="968" duration="240"/>
   <frame tileid="964" duration="240"/>
  </animation>
 </tile>
 <tile id="961">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="961" duration="240"/>
   <frame tileid="965" duration="240"/>
   <frame tileid="969" duration="240"/>
   <frame tileid="973" duration="240"/>
   <frame tileid="969" duration="240"/>
   <frame tileid="965" duration="240"/>
  </animation>
 </tile>
 <tile id="962">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="962" duration="240"/>
   <frame tileid="966" duration="240"/>
   <frame tileid="970" duration="240"/>
   <frame tileid="974" duration="240"/>
   <frame tileid="970" duration="240"/>
   <frame tileid="966" duration="240"/>
  </animation>
 </tile>
 <tile id="963">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="963" duration="240"/>
   <frame tileid="967" duration="240"/>
   <frame tileid="971" duration="240"/>
   <frame tileid="975" duration="240"/>
   <frame tileid="971" duration="240"/>
   <frame tileid="967" duration="240"/>
  </animation>
 </tile>
 <tile id="964">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="965">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="966">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="967">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="968">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="969">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="970">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="971">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="972">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="973">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="974">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="975">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="976" terrain="1,10,1,10">
  <properties>
   <property name="type" value="swamp"/>
  </properties>
 </tile>
 <tile id="977" terrain="10,10,10,10">
  <properties>
   <property name="type" value="swamp"/>
  </properties>
 </tile>
 <tile id="978" terrain="10,1,10,1">
  <properties>
   <property name="type" value="swamp"/>
  </properties>
 </tile>
 <tile id="979">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="980">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="980" duration="240"/>
   <frame tileid="984" duration="240"/>
   <frame tileid="988" duration="240"/>
   <frame tileid="992" duration="240"/>
   <frame tileid="988" duration="240"/>
   <frame tileid="984" duration="240"/>
  </animation>
 </tile>
 <tile id="981">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="981" duration="240"/>
   <frame tileid="985" duration="240"/>
   <frame tileid="989" duration="240"/>
   <frame tileid="993" duration="240"/>
   <frame tileid="989" duration="240"/>
   <frame tileid="985" duration="240"/>
  </animation>
 </tile>
 <tile id="982">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="982" duration="240"/>
   <frame tileid="986" duration="240"/>
   <frame tileid="990" duration="240"/>
   <frame tileid="994" duration="240"/>
   <frame tileid="990" duration="240"/>
   <frame tileid="986" duration="240"/>
  </animation>
 </tile>
 <tile id="983">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="983" duration="240"/>
   <frame tileid="987" duration="240"/>
   <frame tileid="991" duration="240"/>
   <frame tileid="995" duration="240"/>
   <frame tileid="991" duration="240"/>
   <frame tileid="987" duration="240"/>
  </animation>
 </tile>
 <tile id="984">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="985">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="986">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="987">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="988">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="989">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="990">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="991">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="992">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="993">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="994">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="995">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="996">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="997">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="998">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="999">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="1000">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1000" duration="240"/>
   <frame tileid="1004" duration="240"/>
   <frame tileid="1008" duration="240"/>
   <frame tileid="1012" duration="240"/>
   <frame tileid="1008" duration="240"/>
   <frame tileid="1004" duration="240"/>
  </animation>
 </tile>
 <tile id="1001">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1001" duration="240"/>
   <frame tileid="1005" duration="240"/>
   <frame tileid="1009" duration="240"/>
   <frame tileid="1013" duration="240"/>
   <frame tileid="1009" duration="240"/>
   <frame tileid="1005" duration="240"/>
  </animation>
 </tile>
 <tile id="1002">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1002" duration="240"/>
   <frame tileid="1006" duration="240"/>
   <frame tileid="1010" duration="240"/>
   <frame tileid="1014" duration="240"/>
   <frame tileid="1010" duration="240"/>
   <frame tileid="1006" duration="240"/>
  </animation>
 </tile>
 <tile id="1003">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1003" duration="240"/>
   <frame tileid="1007" duration="240"/>
   <frame tileid="1011" duration="240"/>
   <frame tileid="1015" duration="240"/>
   <frame tileid="1011" duration="240"/>
   <frame tileid="1007" duration="240"/>
  </animation>
 </tile>
 <tile id="1004">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1005">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1006">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1007">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1008">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1009">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1010">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1011">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1012">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1013">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1014">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1015">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1016" terrain="1,10,1,1">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="1017" terrain="10,10,1,1">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="1018" terrain="10,1,1,1">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="1019">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="1020">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1020" duration="240"/>
   <frame tileid="1024" duration="240"/>
   <frame tileid="1028" duration="240"/>
   <frame tileid="1032" duration="240"/>
   <frame tileid="1028" duration="240"/>
   <frame tileid="1024" duration="240"/>
  </animation>
 </tile>
 <tile id="1021">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1021" duration="240"/>
   <frame tileid="1025" duration="240"/>
   <frame tileid="1029" duration="240"/>
   <frame tileid="1033" duration="240"/>
   <frame tileid="1029" duration="240"/>
   <frame tileid="1025" duration="240"/>
  </animation>
 </tile>
 <tile id="1022">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1022" duration="240"/>
   <frame tileid="1026" duration="240"/>
   <frame tileid="1030" duration="240"/>
   <frame tileid="1034" duration="240"/>
   <frame tileid="1030" duration="240"/>
   <frame tileid="1026" duration="240"/>
  </animation>
 </tile>
 <tile id="1023">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1023" duration="240"/>
   <frame tileid="1027" duration="240"/>
   <frame tileid="1031" duration="240"/>
   <frame tileid="1035" duration="240"/>
   <frame tileid="1031" duration="240"/>
   <frame tileid="1027" duration="240"/>
  </animation>
 </tile>
 <tile id="1024">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1025">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1026">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1027">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1028">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1029">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1030">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1031">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1032">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1033">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1034">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1035">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1036">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="1037">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="1038">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="1039">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="1040">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1040" duration="240"/>
   <frame tileid="1044" duration="240"/>
   <frame tileid="1048" duration="240"/>
   <frame tileid="1052" duration="240"/>
   <frame tileid="1048" duration="240"/>
   <frame tileid="1044" duration="240"/>
   <frame tileid="1040" duration="240"/>
  </animation>
 </tile>
 <tile id="1041">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1041" duration="240"/>
   <frame tileid="1045" duration="240"/>
   <frame tileid="1049" duration="240"/>
   <frame tileid="1053" duration="240"/>
   <frame tileid="1049" duration="240"/>
   <frame tileid="1045" duration="240"/>
  </animation>
 </tile>
 <tile id="1042">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1042" duration="240"/>
   <frame tileid="1046" duration="240"/>
   <frame tileid="1050" duration="240"/>
   <frame tileid="1054" duration="240"/>
   <frame tileid="1050" duration="240"/>
   <frame tileid="1046" duration="240"/>
  </animation>
 </tile>
 <tile id="1043">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1043" duration="240"/>
   <frame tileid="1047" duration="240"/>
   <frame tileid="1051" duration="240"/>
   <frame tileid="1055" duration="240"/>
   <frame tileid="1051" duration="240"/>
   <frame tileid="1047" duration="240"/>
  </animation>
 </tile>
 <tile id="1044">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1045">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1046">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1047">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1048">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1049">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1050">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1051">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1052">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1053">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1054">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1055">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1056" terrain="1,10,10,10">
  <properties>
   <property name="type" value="swamp"/>
  </properties>
 </tile>
 <tile id="1057" terrain="10,1,10,10">
  <properties>
   <property name="type" value="swamp"/>
  </properties>
 </tile>
 <tile id="1058" terrain="1,10,10,1">
  <properties>
   <property name="type" value="swamp"/>
  </properties>
 </tile>
 <tile id="1059" terrain="10,1,1,10">
  <properties>
   <property name="type" value="swamp"/>
  </properties>
 </tile>
 <tile id="1060">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1060" duration="240"/>
   <frame tileid="1064" duration="240"/>
   <frame tileid="1068" duration="240"/>
   <frame tileid="1072" duration="240"/>
   <frame tileid="1068" duration="240"/>
   <frame tileid="1064" duration="240"/>
  </animation>
 </tile>
 <tile id="1061">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1061" duration="240"/>
   <frame tileid="1065" duration="240"/>
   <frame tileid="1069" duration="240"/>
   <frame tileid="1073" duration="240"/>
   <frame tileid="1069" duration="240"/>
   <frame tileid="1065" duration="240"/>
  </animation>
 </tile>
 <tile id="1062">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1062" duration="240"/>
   <frame tileid="1066" duration="240"/>
   <frame tileid="1070" duration="240"/>
   <frame tileid="1074" duration="240"/>
   <frame tileid="1070" duration="240"/>
   <frame tileid="1066" duration="240"/>
  </animation>
 </tile>
 <tile id="1063">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1063" duration="240"/>
   <frame tileid="1067" duration="240"/>
   <frame tileid="1071" duration="240"/>
   <frame tileid="1075" duration="240"/>
   <frame tileid="1071" duration="240"/>
   <frame tileid="1067" duration="240"/>
  </animation>
 </tile>
 <tile id="1064">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1065">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1066">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1067">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1068">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1069">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1070">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1071">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1072">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1073">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1074">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1075">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1076">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="1077">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="1078">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="1079">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="1080">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1080" duration="240"/>
   <frame tileid="1084" duration="240"/>
   <frame tileid="1088" duration="240"/>
   <frame tileid="1092" duration="240"/>
   <frame tileid="1088" duration="240"/>
   <frame tileid="1084" duration="240"/>
  </animation>
 </tile>
 <tile id="1081">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1081" duration="240"/>
   <frame tileid="1085" duration="240"/>
   <frame tileid="1089" duration="240"/>
   <frame tileid="1093" duration="240"/>
   <frame tileid="1089" duration="240"/>
   <frame tileid="1085" duration="240"/>
  </animation>
 </tile>
 <tile id="1082">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1082" duration="240"/>
   <frame tileid="1086" duration="240"/>
   <frame tileid="1090" duration="240"/>
   <frame tileid="1094" duration="240"/>
   <frame tileid="1090" duration="240"/>
   <frame tileid="1086" duration="240"/>
  </animation>
 </tile>
 <tile id="1083">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1083" duration="240"/>
   <frame tileid="1087" duration="240"/>
   <frame tileid="1091" duration="240"/>
   <frame tileid="1095" duration="240"/>
   <frame tileid="1091" duration="240"/>
   <frame tileid="1087" duration="240"/>
  </animation>
 </tile>
 <tile id="1084">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1085">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1086">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1087">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1088">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1089">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1090">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1091">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1092">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1093">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1094">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1095">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1096" terrain="10,10,1,10">
  <properties>
   <property name="type" value="swamp"/>
  </properties>
 </tile>
 <tile id="1097" terrain="10,10,10,1">
  <properties>
   <property name="type" value="swamp"/>
  </properties>
 </tile>
 <tile id="1098">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="1099">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="1100">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1100" duration="240"/>
   <frame tileid="1104" duration="240"/>
   <frame tileid="1108" duration="240"/>
   <frame tileid="1112" duration="240"/>
   <frame tileid="1108" duration="240"/>
   <frame tileid="1104" duration="240"/>
  </animation>
 </tile>
 <tile id="1101">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1101" duration="240"/>
   <frame tileid="1105" duration="240"/>
   <frame tileid="1109" duration="240"/>
   <frame tileid="1113" duration="240"/>
   <frame tileid="1109" duration="240"/>
   <frame tileid="1105" duration="240"/>
  </animation>
 </tile>
 <tile id="1102">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1102" duration="240"/>
   <frame tileid="1106" duration="240"/>
   <frame tileid="1110" duration="240"/>
   <frame tileid="1114" duration="240"/>
   <frame tileid="1110" duration="240"/>
   <frame tileid="1106" duration="240"/>
  </animation>
 </tile>
 <tile id="1103">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1103" duration="240"/>
   <frame tileid="1107" duration="240"/>
   <frame tileid="1111" duration="240"/>
   <frame tileid="1115" duration="240"/>
   <frame tileid="1111" duration="240"/>
   <frame tileid="1107" duration="240"/>
  </animation>
 </tile>
 <tile id="1104">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1105">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1106">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1107">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1108">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1109">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1110">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1111">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1112">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1113">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1114">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1115">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1116">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="1117">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="1118">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="1119">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="1120">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1120" duration="240"/>
   <frame tileid="1124" duration="240"/>
   <frame tileid="1128" duration="240"/>
   <frame tileid="1132" duration="240"/>
   <frame tileid="1128" duration="240"/>
   <frame tileid="1124" duration="240"/>
  </animation>
 </tile>
 <tile id="1121">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1121" duration="240"/>
   <frame tileid="1125" duration="240"/>
   <frame tileid="1129" duration="240"/>
   <frame tileid="1133" duration="240"/>
   <frame tileid="1129" duration="240"/>
   <frame tileid="1125" duration="240"/>
  </animation>
 </tile>
 <tile id="1122">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1122" duration="240"/>
   <frame tileid="1126" duration="240"/>
   <frame tileid="1130" duration="240"/>
   <frame tileid="1134" duration="240"/>
   <frame tileid="1130" duration="240"/>
   <frame tileid="1126" duration="240"/>
  </animation>
 </tile>
 <tile id="1123">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1123" duration="240"/>
   <frame tileid="1127" duration="240"/>
   <frame tileid="1131" duration="240"/>
   <frame tileid="1135" duration="240"/>
   <frame tileid="1131" duration="240"/>
   <frame tileid="1127" duration="240"/>
  </animation>
 </tile>
 <tile id="1124">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1125">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1126">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1127">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1128">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1129">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1130">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1131">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1132">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1133">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1134">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1135">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1136" terrain="5,5,1,10">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1137" terrain="5,5,10,1">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1138" terrain="5,1,5,10">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1139" terrain="1,5,10,5">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1140">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1140" duration="240"/>
   <frame tileid="1144" duration="240"/>
   <frame tileid="1148" duration="240"/>
   <frame tileid="1152" duration="240"/>
   <frame tileid="1148" duration="240"/>
   <frame tileid="1144" duration="240"/>
  </animation>
 </tile>
 <tile id="1141">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1141" duration="240"/>
   <frame tileid="1145" duration="240"/>
   <frame tileid="1149" duration="240"/>
   <frame tileid="1153" duration="240"/>
   <frame tileid="1149" duration="240"/>
   <frame tileid="1145" duration="240"/>
  </animation>
 </tile>
 <tile id="1142">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1142" duration="240"/>
   <frame tileid="1146" duration="240"/>
   <frame tileid="1150" duration="240"/>
   <frame tileid="1154" duration="240"/>
   <frame tileid="1150" duration="240"/>
   <frame tileid="1146" duration="240"/>
  </animation>
 </tile>
 <tile id="1143">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1143" duration="240"/>
   <frame tileid="1147" duration="240"/>
   <frame tileid="1151" duration="240"/>
   <frame tileid="1155" duration="240"/>
   <frame tileid="1151" duration="240"/>
   <frame tileid="1147" duration="240"/>
  </animation>
 </tile>
 <tile id="1144">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1145">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1146">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1147">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1148">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1149">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1150">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1151">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1152">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1153">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1154">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1155">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1156">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="1157">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="1158">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="1159">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="1160">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1160" duration="240"/>
   <frame tileid="1164" duration="240"/>
   <frame tileid="1168" duration="240"/>
   <frame tileid="1172" duration="240"/>
   <frame tileid="1168" duration="240"/>
   <frame tileid="1164" duration="240"/>
  </animation>
 </tile>
 <tile id="1161">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1161" duration="240"/>
   <frame tileid="1165" duration="240"/>
   <frame tileid="1169" duration="240"/>
   <frame tileid="1173" duration="240"/>
   <frame tileid="1169" duration="240"/>
   <frame tileid="1165" duration="240"/>
  </animation>
 </tile>
 <tile id="1162">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1162" duration="240"/>
   <frame tileid="1166" duration="240"/>
   <frame tileid="1170" duration="240"/>
   <frame tileid="1174" duration="240"/>
   <frame tileid="1170" duration="240"/>
   <frame tileid="1166" duration="240"/>
  </animation>
 </tile>
 <tile id="1163">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1163" duration="240"/>
   <frame tileid="1167" duration="240"/>
   <frame tileid="1171" duration="240"/>
   <frame tileid="1175" duration="240"/>
   <frame tileid="1171" duration="240"/>
   <frame tileid="1167" duration="240"/>
  </animation>
 </tile>
 <tile id="1164">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1165">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1166">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1167">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1168">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1169">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1170">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1171">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1172">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1173">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1174">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1175">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1176" terrain="1,10,5,5">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1177" terrain="10,1,5,5">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1178" terrain="5,10,5,1">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1179" terrain="10,5,1,5">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1180">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1180" duration="240"/>
   <frame tileid="1184" duration="240"/>
   <frame tileid="1188" duration="240"/>
   <frame tileid="1192" duration="240"/>
   <frame tileid="1188" duration="240"/>
   <frame tileid="1184" duration="240"/>
  </animation>
 </tile>
 <tile id="1181">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1181" duration="240"/>
   <frame tileid="1185" duration="240"/>
   <frame tileid="1189" duration="240"/>
   <frame tileid="1193" duration="240"/>
   <frame tileid="1189" duration="240"/>
   <frame tileid="1185" duration="240"/>
  </animation>
 </tile>
 <tile id="1182">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1182" duration="240"/>
   <frame tileid="1186" duration="240"/>
   <frame tileid="1190" duration="240"/>
   <frame tileid="1194" duration="240"/>
   <frame tileid="1190" duration="240"/>
   <frame tileid="1186" duration="240"/>
  </animation>
 </tile>
 <tile id="1183">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1183" duration="240"/>
   <frame tileid="1187" duration="240"/>
   <frame tileid="1191" duration="240"/>
   <frame tileid="1195" duration="240"/>
   <frame tileid="1191" duration="240"/>
   <frame tileid="1187" duration="240"/>
  </animation>
 </tile>
 <tile id="1184">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1185">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1186">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1187">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1188">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1189">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1190">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1191">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1192">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1193">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1194">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1195">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1196">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="1197">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="1198">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="1199">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="1200">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1200" duration="240"/>
   <frame tileid="1204" duration="240"/>
   <frame tileid="1208" duration="240"/>
   <frame tileid="1212" duration="240"/>
   <frame tileid="1208" duration="240"/>
   <frame tileid="1204" duration="240"/>
  </animation>
 </tile>
 <tile id="1201">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1201" duration="240"/>
   <frame tileid="1205" duration="240"/>
   <frame tileid="1209" duration="240"/>
   <frame tileid="1213" duration="240"/>
   <frame tileid="1209" duration="240"/>
   <frame tileid="1205" duration="240"/>
  </animation>
 </tile>
 <tile id="1202">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1202" duration="240"/>
   <frame tileid="1206" duration="240"/>
   <frame tileid="1210" duration="240"/>
   <frame tileid="1214" duration="240"/>
   <frame tileid="1210" duration="240"/>
   <frame tileid="1206" duration="240"/>
  </animation>
 </tile>
 <tile id="1203">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1203" duration="240"/>
   <frame tileid="1207" duration="240"/>
   <frame tileid="1211" duration="240"/>
   <frame tileid="1215" duration="240"/>
   <frame tileid="1211" duration="240"/>
   <frame tileid="1207" duration="240"/>
   <frame tileid="1203" duration="240"/>
  </animation>
 </tile>
 <tile id="1204">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1205">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1206">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1207">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1208">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1209">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1210">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1211">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1212">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1213">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1214">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1215">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1216" terrain="10,10,10,5">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1217" terrain="10,10,5,5">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1218" terrain="10,10,5,10">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1219">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="1220">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1220" duration="240"/>
   <frame tileid="1224" duration="240"/>
   <frame tileid="1228" duration="240"/>
   <frame tileid="1232" duration="240"/>
   <frame tileid="1228" duration="240"/>
   <frame tileid="1224" duration="240"/>
  </animation>
 </tile>
 <tile id="1221">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1221" duration="240"/>
   <frame tileid="1225" duration="240"/>
   <frame tileid="1229" duration="240"/>
   <frame tileid="1233" duration="240"/>
   <frame tileid="1229" duration="240"/>
   <frame tileid="1225" duration="240"/>
  </animation>
 </tile>
 <tile id="1222">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1222" duration="240"/>
   <frame tileid="1226" duration="240"/>
   <frame tileid="1230" duration="240"/>
   <frame tileid="1234" duration="240"/>
   <frame tileid="1230" duration="240"/>
   <frame tileid="1226" duration="240"/>
  </animation>
 </tile>
 <tile id="1223">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1223" duration="240"/>
   <frame tileid="1227" duration="240"/>
   <frame tileid="1231" duration="240"/>
   <frame tileid="1235" duration="240"/>
   <frame tileid="1231" duration="240"/>
   <frame tileid="1227" duration="240"/>
  </animation>
 </tile>
 <tile id="1224">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1225">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1226">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1227">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1228">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1229">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1230">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1231">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1232">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1233">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1234">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1235">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1236">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="1237">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="1238">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="1239">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="1240">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1240" duration="240"/>
   <frame tileid="1244" duration="240"/>
   <frame tileid="1248" duration="240"/>
   <frame tileid="1252" duration="240"/>
   <frame tileid="1248" duration="240"/>
   <frame tileid="1244" duration="240"/>
  </animation>
 </tile>
 <tile id="1241">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1241" duration="240"/>
   <frame tileid="1245" duration="240"/>
   <frame tileid="1249" duration="240"/>
   <frame tileid="1253" duration="240"/>
   <frame tileid="1249" duration="240"/>
   <frame tileid="1245" duration="240"/>
  </animation>
 </tile>
 <tile id="1242">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1242" duration="240"/>
   <frame tileid="1246" duration="240"/>
   <frame tileid="1250" duration="240"/>
   <frame tileid="1254" duration="240"/>
   <frame tileid="1250" duration="240"/>
   <frame tileid="1246" duration="240"/>
  </animation>
 </tile>
 <tile id="1243">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1243" duration="240"/>
   <frame tileid="1247" duration="240"/>
   <frame tileid="1251" duration="240"/>
   <frame tileid="1255" duration="240"/>
   <frame tileid="1251" duration="240"/>
   <frame tileid="1247" duration="240"/>
  </animation>
 </tile>
 <tile id="1244">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1245">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1246">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1247">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1248">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1249">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1250">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1251">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1252">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1253">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1254">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1255">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1256" terrain="10,5,10,5">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1257" terrain="5,5,5,5">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="1258" terrain="5,10,5,10">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1259">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="1260">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1260" duration="240"/>
   <frame tileid="1264" duration="240"/>
   <frame tileid="1268" duration="240"/>
   <frame tileid="1272" duration="240"/>
   <frame tileid="1268" duration="240"/>
   <frame tileid="1264" duration="240"/>
  </animation>
 </tile>
 <tile id="1261">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1261" duration="240"/>
   <frame tileid="1265" duration="240"/>
   <frame tileid="1269" duration="240"/>
   <frame tileid="1273" duration="240"/>
   <frame tileid="1269" duration="240"/>
   <frame tileid="1265" duration="240"/>
  </animation>
 </tile>
 <tile id="1262">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1262" duration="240"/>
   <frame tileid="1266" duration="240"/>
   <frame tileid="1270" duration="240"/>
   <frame tileid="1274" duration="240"/>
   <frame tileid="1270" duration="240"/>
   <frame tileid="1266" duration="240"/>
  </animation>
 </tile>
 <tile id="1263">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1263" duration="240"/>
   <frame tileid="1267" duration="240"/>
   <frame tileid="1271" duration="240"/>
   <frame tileid="1275" duration="240"/>
   <frame tileid="1271" duration="240"/>
   <frame tileid="1267" duration="240"/>
  </animation>
 </tile>
 <tile id="1264">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1265">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1266">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1267">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1268">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1269">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1270">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1271">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1272">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1273">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1274">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1275">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1276">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="1277">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="1278">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="1279">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="1280">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1280" duration="240"/>
   <frame tileid="1284" duration="240"/>
   <frame tileid="1288" duration="240"/>
   <frame tileid="1292" duration="240"/>
   <frame tileid="1288" duration="240"/>
   <frame tileid="1284" duration="240"/>
  </animation>
 </tile>
 <tile id="1281">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1281" duration="240"/>
   <frame tileid="1285" duration="240"/>
   <frame tileid="1289" duration="240"/>
   <frame tileid="1293" duration="240"/>
   <frame tileid="1289" duration="240"/>
   <frame tileid="1285" duration="240"/>
  </animation>
 </tile>
 <tile id="1282">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1282" duration="240"/>
   <frame tileid="1286" duration="240"/>
   <frame tileid="1290" duration="240"/>
   <frame tileid="1294" duration="240"/>
   <frame tileid="1290" duration="240"/>
   <frame tileid="1286" duration="240"/>
  </animation>
 </tile>
 <tile id="1283">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1283" duration="240"/>
   <frame tileid="1287" duration="240"/>
   <frame tileid="1291" duration="240"/>
   <frame tileid="1295" duration="240"/>
   <frame tileid="1291" duration="240"/>
   <frame tileid="1287" duration="240"/>
   <frame tileid="1283" duration="240"/>
  </animation>
 </tile>
 <tile id="1284">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1285">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1286">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1287">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1288">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1289">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1290">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1291">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1292">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1293">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1294">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1295">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1296" terrain="10,5,10,10">
  <properties>
   <property name="type" value="swamp"/>
  </properties>
 </tile>
 <tile id="1297" terrain="5,5,10,10">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1298" terrain="5,10,10,10">
  <properties>
   <property name="type" value="swamp"/>
  </properties>
 </tile>
 <tile id="1299">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="1300">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1300" duration="240"/>
   <frame tileid="1304" duration="240"/>
   <frame tileid="1308" duration="240"/>
   <frame tileid="1312" duration="240"/>
   <frame tileid="1308" duration="240"/>
   <frame tileid="1304" duration="240"/>
  </animation>
 </tile>
 <tile id="1301">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1301" duration="240"/>
   <frame tileid="1305" duration="240"/>
   <frame tileid="1309" duration="240"/>
   <frame tileid="1313" duration="240"/>
   <frame tileid="1309" duration="240"/>
   <frame tileid="1305" duration="240"/>
  </animation>
 </tile>
 <tile id="1302">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1302" duration="240"/>
   <frame tileid="1306" duration="240"/>
   <frame tileid="1310" duration="240"/>
   <frame tileid="1314" duration="240"/>
   <frame tileid="1310" duration="240"/>
   <frame tileid="1306" duration="240"/>
  </animation>
 </tile>
 <tile id="1303">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1303" duration="240"/>
   <frame tileid="1307" duration="240"/>
   <frame tileid="1311" duration="240"/>
   <frame tileid="1315" duration="240"/>
   <frame tileid="1311" duration="240"/>
   <frame tileid="1307" duration="240"/>
  </animation>
 </tile>
 <tile id="1304">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1305">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1306">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1307">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1308">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1309">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1310">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1311">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1312">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1313">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1314">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1315">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1316">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="1317">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="1318">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="1319">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="1320">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1320" duration="240"/>
   <frame tileid="1324" duration="240"/>
   <frame tileid="1328" duration="240"/>
   <frame tileid="1332" duration="240"/>
   <frame tileid="1328" duration="240"/>
   <frame tileid="1324" duration="240"/>
  </animation>
 </tile>
 <tile id="1321">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1321" duration="240"/>
   <frame tileid="1325" duration="240"/>
   <frame tileid="1329" duration="240"/>
   <frame tileid="1333" duration="240"/>
   <frame tileid="1329" duration="240"/>
   <frame tileid="1325" duration="240"/>
  </animation>
 </tile>
 <tile id="1322">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1322" duration="240"/>
   <frame tileid="1326" duration="240"/>
   <frame tileid="1330" duration="240"/>
   <frame tileid="1334" duration="240"/>
   <frame tileid="1330" duration="240"/>
   <frame tileid="1326" duration="240"/>
  </animation>
 </tile>
 <tile id="1323">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1323" duration="240"/>
   <frame tileid="1327" duration="240"/>
   <frame tileid="1331" duration="240"/>
   <frame tileid="1335" duration="240"/>
   <frame tileid="1331" duration="240"/>
   <frame tileid="1327" duration="240"/>
  </animation>
 </tile>
 <tile id="1324">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1325">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1326">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1327">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1328">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1329">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1330">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1331">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1332">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1333">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1334">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1335">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1336" terrain="10,5,5,5">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1337" terrain="5,10,5,5">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1338">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="1339">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="1340">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1340" duration="240"/>
   <frame tileid="1344" duration="240"/>
   <frame tileid="1348" duration="240"/>
   <frame tileid="1352" duration="240"/>
   <frame tileid="1348" duration="240"/>
   <frame tileid="1344" duration="240"/>
  </animation>
 </tile>
 <tile id="1341">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1341" duration="240"/>
   <frame tileid="1345" duration="240"/>
   <frame tileid="1349" duration="240"/>
   <frame tileid="1353" duration="240"/>
   <frame tileid="1349" duration="240"/>
   <frame tileid="1345" duration="240"/>
  </animation>
 </tile>
 <tile id="1342">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1342" duration="240"/>
   <frame tileid="1346" duration="240"/>
   <frame tileid="1350" duration="240"/>
   <frame tileid="1354" duration="240"/>
   <frame tileid="1350" duration="240"/>
   <frame tileid="1346" duration="240"/>
  </animation>
 </tile>
 <tile id="1343">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1343" duration="240"/>
   <frame tileid="1347" duration="240"/>
   <frame tileid="1351" duration="240"/>
   <frame tileid="1355" duration="240"/>
   <frame tileid="1351" duration="240"/>
   <frame tileid="1347" duration="240"/>
  </animation>
 </tile>
 <tile id="1344">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1345">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1346">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1347">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1348">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1349">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1350">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1351">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1352">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1353">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1354">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1355">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1356">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="1357">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="1358">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="1359">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="1360">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1360" duration="240"/>
   <frame tileid="1364" duration="240"/>
   <frame tileid="1368" duration="240"/>
   <frame tileid="1372" duration="240"/>
   <frame tileid="1368" duration="240"/>
   <frame tileid="1364" duration="240"/>
  </animation>
 </tile>
 <tile id="1361">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1361" duration="240"/>
   <frame tileid="1365" duration="240"/>
   <frame tileid="1369" duration="240"/>
   <frame tileid="1373" duration="240"/>
   <frame tileid="1369" duration="240"/>
   <frame tileid="1365" duration="240"/>
  </animation>
 </tile>
 <tile id="1362">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1362" duration="240"/>
   <frame tileid="1366" duration="240"/>
   <frame tileid="1370" duration="240"/>
   <frame tileid="1374" duration="240"/>
   <frame tileid="1370" duration="240"/>
   <frame tileid="1366" duration="240"/>
  </animation>
 </tile>
 <tile id="1363">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1363" duration="240"/>
   <frame tileid="1367" duration="240"/>
   <frame tileid="1371" duration="240"/>
   <frame tileid="1375" duration="240"/>
   <frame tileid="1371" duration="240"/>
   <frame tileid="1367" duration="240"/>
  </animation>
 </tile>
 <tile id="1364">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1365">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1366">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1367">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1368">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1369">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1370">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1371">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1372">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1373">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1374">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1375">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1376" terrain="5,5,10,5">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1377" terrain="5,5,5,10">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1378">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="1379">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="1380">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1380" duration="240"/>
   <frame tileid="1384" duration="240"/>
   <frame tileid="1388" duration="240"/>
   <frame tileid="1392" duration="240"/>
   <frame tileid="1388" duration="240"/>
   <frame tileid="1384" duration="240"/>
  </animation>
 </tile>
 <tile id="1381">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1381" duration="240"/>
   <frame tileid="1385" duration="240"/>
   <frame tileid="1389" duration="240"/>
   <frame tileid="1393" duration="240"/>
   <frame tileid="1389" duration="240"/>
   <frame tileid="1385" duration="240"/>
  </animation>
 </tile>
 <tile id="1382">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1382" duration="240"/>
   <frame tileid="1386" duration="240"/>
   <frame tileid="1390" duration="240"/>
   <frame tileid="1394" duration="240"/>
   <frame tileid="1390" duration="240"/>
   <frame tileid="1386" duration="240"/>
  </animation>
 </tile>
 <tile id="1383">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1383" duration="240"/>
   <frame tileid="1387" duration="240"/>
   <frame tileid="1391" duration="240"/>
   <frame tileid="1395" duration="240"/>
   <frame tileid="1391" duration="240"/>
   <frame tileid="1387" duration="240"/>
  </animation>
 </tile>
 <tile id="1384">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1385">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1386">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1387">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1388">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1389">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1390">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1391">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1392">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1393">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1394">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1395">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1396" terrain="1,3,3,3">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="1397" terrain="3,1,3,3">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="1398" terrain="1,6,6,6">
  <properties>
   <property name="type" value="desert"/>
  </properties>
 </tile>
 <tile id="1399" terrain="6,1,6,6">
  <properties>
   <property name="type" value="desert"/>
  </properties>
 </tile>
 <tile id="1400">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1400" duration="240"/>
   <frame tileid="1404" duration="240"/>
   <frame tileid="1408" duration="240"/>
   <frame tileid="1412" duration="240"/>
   <frame tileid="1408" duration="240"/>
   <frame tileid="1404" duration="240"/>
  </animation>
 </tile>
 <tile id="1401">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1401" duration="240"/>
   <frame tileid="1405" duration="240"/>
   <frame tileid="1409" duration="240"/>
   <frame tileid="1413" duration="240"/>
   <frame tileid="1409" duration="240"/>
   <frame tileid="1405" duration="240"/>
  </animation>
 </tile>
 <tile id="1402">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1402" duration="240"/>
   <frame tileid="1406" duration="240"/>
   <frame tileid="1410" duration="240"/>
   <frame tileid="1414" duration="240"/>
   <frame tileid="1410" duration="240"/>
   <frame tileid="1406" duration="240"/>
  </animation>
 </tile>
 <tile id="1403">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1403" duration="240"/>
   <frame tileid="1407" duration="240"/>
   <frame tileid="1411" duration="240"/>
   <frame tileid="1415" duration="240"/>
   <frame tileid="1411" duration="240"/>
   <frame tileid="1407" duration="240"/>
   <frame tileid="1403" duration="240"/>
  </animation>
 </tile>
 <tile id="1404">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1405">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1406">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1407">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1408">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1409">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1410">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1411">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1412">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1413">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1414">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1415">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1416" terrain="10,5,5,10">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1417" terrain="5,10,10,5">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1418">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="1419">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="1420">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1420" duration="240"/>
   <frame tileid="1424" duration="240"/>
   <frame tileid="1428" duration="240"/>
   <frame tileid="1432" duration="240"/>
   <frame tileid="1428" duration="240"/>
   <frame tileid="1424" duration="240"/>
  </animation>
 </tile>
 <tile id="1421">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1421" duration="240"/>
   <frame tileid="1425" duration="240"/>
   <frame tileid="1429" duration="240"/>
   <frame tileid="1433" duration="240"/>
   <frame tileid="1429" duration="240"/>
   <frame tileid="1425" duration="240"/>
  </animation>
 </tile>
 <tile id="1422">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1422" duration="240"/>
   <frame tileid="1426" duration="240"/>
   <frame tileid="1430" duration="240"/>
   <frame tileid="1434" duration="240"/>
   <frame tileid="1430" duration="240"/>
   <frame tileid="1426" duration="240"/>
  </animation>
 </tile>
 <tile id="1423">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1423" duration="240"/>
   <frame tileid="1427" duration="240"/>
   <frame tileid="1431" duration="240"/>
   <frame tileid="1435" duration="240"/>
   <frame tileid="1431" duration="240"/>
   <frame tileid="1427" duration="240"/>
  </animation>
 </tile>
 <tile id="1424">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1425">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1426">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1427">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1428">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1429">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1430">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1431">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1432">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1433">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1434">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1435">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1436" terrain="3,3,1,3">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="1437" terrain="3,3,3,1">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="1438" terrain="6,6,1,6">
  <properties>
   <property name="type" value="desert"/>
  </properties>
 </tile>
 <tile id="1439" terrain="6,6,6,1">
  <properties>
   <property name="type" value="desert"/>
  </properties>
 </tile>
 <tile id="1440">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1440" duration="240"/>
   <frame tileid="1444" duration="240"/>
   <frame tileid="1448" duration="240"/>
   <frame tileid="1452" duration="240"/>
   <frame tileid="1448" duration="240"/>
   <frame tileid="1444" duration="240"/>
  </animation>
 </tile>
 <tile id="1441">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1441" duration="240"/>
   <frame tileid="1445" duration="240"/>
   <frame tileid="1449" duration="240"/>
   <frame tileid="1453" duration="240"/>
   <frame tileid="1449" duration="240"/>
   <frame tileid="1445" duration="240"/>
  </animation>
 </tile>
 <tile id="1442">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1442" duration="240"/>
   <frame tileid="1446" duration="240"/>
   <frame tileid="1450" duration="240"/>
   <frame tileid="1454" duration="240"/>
   <frame tileid="1450" duration="240"/>
   <frame tileid="1446" duration="240"/>
  </animation>
 </tile>
 <tile id="1443">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1443" duration="240"/>
   <frame tileid="1447" duration="240"/>
   <frame tileid="1451" duration="240"/>
   <frame tileid="1455" duration="240"/>
   <frame tileid="1451" duration="240"/>
   <frame tileid="1447" duration="240"/>
  </animation>
 </tile>
 <tile id="1444">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1445">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1446">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1447">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1448">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1449">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1450">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1451">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1452">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1453">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1454">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1455">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1456">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="1457">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="1458">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="1459">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="1460">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1460" duration="240"/>
   <frame tileid="1464" duration="240"/>
   <frame tileid="1468" duration="240"/>
   <frame tileid="1472" duration="240"/>
   <frame tileid="1468" duration="240"/>
   <frame tileid="1464" duration="240"/>
  </animation>
 </tile>
 <tile id="1461">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1461" duration="240"/>
   <frame tileid="1465" duration="240"/>
   <frame tileid="1469" duration="240"/>
   <frame tileid="1473" duration="240"/>
   <frame tileid="1469" duration="240"/>
   <frame tileid="1465" duration="240"/>
  </animation>
 </tile>
 <tile id="1462">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1462" duration="240"/>
   <frame tileid="1466" duration="240"/>
   <frame tileid="1470" duration="240"/>
   <frame tileid="1474" duration="240"/>
   <frame tileid="1470" duration="240"/>
   <frame tileid="1466" duration="240"/>
  </animation>
 </tile>
 <tile id="1463">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1463" duration="240"/>
   <frame tileid="1467" duration="240"/>
   <frame tileid="1471" duration="240"/>
   <frame tileid="1475" duration="240"/>
   <frame tileid="1471" duration="240"/>
   <frame tileid="1467" duration="240"/>
  </animation>
 </tile>
 <tile id="1464">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1465">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1466">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1467">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1468">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1469">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1470">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1471">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1472">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1473">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1474">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1475">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1476" terrain="1,3,3,1">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="1477" terrain="3,1,1,3">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="1478" terrain="1,6,6,1">
  <properties>
   <property name="type" value="desert"/>
  </properties>
 </tile>
 <tile id="1479" terrain="6,1,1,6">
  <properties>
   <property name="type" value="desert"/>
  </properties>
 </tile>
 <tile id="1480">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1480" duration="240"/>
   <frame tileid="1484" duration="240"/>
   <frame tileid="1488" duration="240"/>
   <frame tileid="1492" duration="240"/>
   <frame tileid="1488" duration="240"/>
   <frame tileid="1484" duration="240"/>
  </animation>
 </tile>
 <tile id="1481">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1481" duration="240"/>
   <frame tileid="1485" duration="240"/>
   <frame tileid="1489" duration="240"/>
   <frame tileid="1493" duration="240"/>
   <frame tileid="1489" duration="240"/>
   <frame tileid="1485" duration="240"/>
  </animation>
 </tile>
 <tile id="1482">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1482" duration="240"/>
   <frame tileid="1486" duration="240"/>
   <frame tileid="1490" duration="240"/>
   <frame tileid="1494" duration="240"/>
   <frame tileid="1490" duration="240"/>
   <frame tileid="1486" duration="240"/>
  </animation>
 </tile>
 <tile id="1483">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1483" duration="240"/>
   <frame tileid="1487" duration="240"/>
   <frame tileid="1491" duration="240"/>
   <frame tileid="1495" duration="240"/>
   <frame tileid="1491" duration="240"/>
   <frame tileid="1487" duration="240"/>
  </animation>
 </tile>
 <tile id="1484">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1485">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1486">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1487">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1488">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1489">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1490">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1491">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1492">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1493">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1494">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1495">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1496">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="1497">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="1498">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="1499">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="1500">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1500" duration="240"/>
   <frame tileid="1504" duration="240"/>
   <frame tileid="1508" duration="240"/>
   <frame tileid="1512" duration="240"/>
   <frame tileid="1508" duration="240"/>
   <frame tileid="1504" duration="240"/>
  </animation>
 </tile>
 <tile id="1501">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1501" duration="240"/>
   <frame tileid="1505" duration="240"/>
   <frame tileid="1509" duration="240"/>
   <frame tileid="1513" duration="240"/>
   <frame tileid="1509" duration="240"/>
   <frame tileid="1505" duration="240"/>
  </animation>
 </tile>
 <tile id="1502">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1502" duration="240"/>
   <frame tileid="1506" duration="240"/>
   <frame tileid="1510" duration="240"/>
   <frame tileid="1514" duration="240"/>
   <frame tileid="1510" duration="240"/>
   <frame tileid="1506" duration="240"/>
  </animation>
 </tile>
 <tile id="1503">
  <properties>
   <property name="type" value="water"/>
  </properties>
  <animation>
   <frame tileid="1503" duration="240"/>
   <frame tileid="1507" duration="240"/>
   <frame tileid="1511" duration="240"/>
   <frame tileid="1515" duration="240"/>
   <frame tileid="1511" duration="240"/>
   <frame tileid="1507" duration="240"/>
  </animation>
 </tile>
 <tile id="1504">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1505">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1506">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1507">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1508">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1509">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1510">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1511">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1512">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1513">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1514">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1515">
  <properties>
   <property name="type" value="water"/>
  </properties>
 </tile>
 <tile id="1516">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="1517">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="1518">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="1519">
  <properties>
   <property name="type" value=""/>
  </properties>
 </tile>
 <tile id="1520" terrain="12,12,12,15"/>
 <tile id="1521" terrain="12,12,15,15"/>
 <tile id="1522" terrain="12,12,15,12"/>
 <tile id="1523" terrain="12,15,15,15"/>
 <tile id="1524" terrain="15,12,15,15"/>
 <tile id="1525" terrain="12,12,12,1"/>
 <tile id="1526" terrain="12,12,1,1"/>
 <tile id="1527" terrain="12,12,1,12"/>
 <tile id="1528" terrain="12,1,1,1"/>
 <tile id="1529" terrain="1,12,1,1"/>
 <tile id="1530" terrain="12,12,12,13">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1531" terrain="12,12,13,13">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1532" terrain="12,12,13,12">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1533" terrain="12,13,13,13">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1534" terrain="13,12,13,13">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1535" terrain="13,13,13,14">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1536" terrain="13,13,14,14">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1537" terrain="13,13,14,13">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1538" terrain="13,14,14,14">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1539" terrain="14,13,14,14">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1540">
  <properties>
   <property name="type" value="bridge"/>
  </properties>
 </tile>
 <tile id="1541">
  <properties>
   <property name="type" value="bridge"/>
  </properties>
 </tile>
 <tile id="1542">
  <properties>
   <property name="type" value="bridge"/>
  </properties>
 </tile>
 <tile id="1543">
  <properties>
   <property name="type" value="bridge"/>
  </properties>
 </tile>
 <tile id="1544">
  <properties>
   <property name="type" value="bridge"/>
  </properties>
 </tile>
 <tile id="1545">
  <properties>
   <property name="type" value="bridge"/>
  </properties>
 </tile>
 <tile id="1560" terrain="12,15,12,15"/>
 <tile id="1561" terrain="15,15,15,15"/>
 <tile id="1562" terrain="15,12,15,12"/>
 <tile id="1563" terrain="15,15,12,15"/>
 <tile id="1564" terrain="15,15,15,12"/>
 <tile id="1565" terrain="12,1,12,1"/>
 <tile id="1567" terrain="1,12,1,12"/>
 <tile id="1568" terrain="1,1,12,1"/>
 <tile id="1569" terrain="1,1,1,12"/>
 <tile id="1570" terrain="12,13,12,13">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1571" terrain="13,13,13,13">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1572" terrain="13,12,13,12">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1573" terrain="13,13,12,13">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1574" terrain="13,13,13,12">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1575" terrain="13,14,13,14">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1576" terrain="14,14,14,14">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1577" terrain="14,13,14,13">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1578" terrain="14,14,13,14">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1579" terrain="14,14,14,13">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1580">
  <properties>
   <property name="type" value="bridge"/>
  </properties>
 </tile>
 <tile id="1581">
  <properties>
   <property name="type" value="bridge"/>
  </properties>
 </tile>
 <tile id="1582">
  <properties>
   <property name="type" value="bridge"/>
  </properties>
 </tile>
 <tile id="1583">
  <properties>
   <property name="type" value="bridge"/>
  </properties>
 </tile>
 <tile id="1584">
  <properties>
   <property name="type" value="bridge"/>
  </properties>
 </tile>
 <tile id="1585">
  <properties>
   <property name="type" value="bridge"/>
  </properties>
 </tile>
 <tile id="1600" terrain="12,15,12,12"/>
 <tile id="1601" terrain="15,15,12,12"/>
 <tile id="1602" terrain="15,12,12,12"/>
 <tile id="1603" terrain="12,15,15,12"/>
 <tile id="1604" terrain="15,12,12,15"/>
 <tile id="1605" terrain="12,1,12,12"/>
 <tile id="1606" terrain="1,1,12,12"/>
 <tile id="1607" terrain="1,12,12,12"/>
 <tile id="1608" terrain="12,1,1,12"/>
 <tile id="1609" terrain="1,12,12,1"/>
 <tile id="1610" terrain="12,13,12,12">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1611" terrain="13,13,12,12">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1612" terrain="13,12,12,12">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1613" terrain="12,13,13,12">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1614" terrain="13,12,12,13">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1615" terrain="13,14,13,13">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1616" terrain="14,14,13,13">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1617" terrain="14,13,13,13">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1618" terrain="13,14,14,13">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1619" terrain="14,13,13,14">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1620">
  <properties>
   <property name="type" value="bridge"/>
  </properties>
 </tile>
 <tile id="1621">
  <properties>
   <property name="type" value="bridge"/>
  </properties>
 </tile>
 <tile id="1622">
  <properties>
   <property name="type" value="bridge"/>
  </properties>
 </tile>
 <tile id="1623">
  <properties>
   <property name="type" value="bridge"/>
  </properties>
 </tile>
 <tile id="1624">
  <properties>
   <property name="type" value="bridge"/>
  </properties>
 </tile>
 <tile id="1625">
  <properties>
   <property name="type" value="bridge"/>
  </properties>
 </tile>
 <tile id="1640" terrain="12,12,12,12"/>
 <tile id="1641" terrain="12,12,12,12" probability="0.03"/>
 <tile id="1642" terrain="12,12,12,12" probability="0.03"/>
 <tile id="1646" terrain="13,13,13,13">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1647" terrain="13,13,13,13" probability="0.1">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1648" terrain="13,13,13,13" probability="0.1">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1649" terrain="13,13,13,13" probability="0.1">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1650" terrain="13,13,13,13" probability="0.05">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1651">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1652">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1653">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1654">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1655">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1656">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1657">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1658" terrain="14,14,14,14" probability="0.025">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1659" terrain="14,14,14,14" probability="0.05">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1660">
  <properties>
   <property name="type" value="bridge"/>
  </properties>
 </tile>
 <tile id="1661">
  <properties>
   <property name="type" value="bridge"/>
  </properties>
 </tile>
 <tile id="1662">
  <properties>
   <property name="type" value="bridge"/>
  </properties>
 </tile>
 <tile id="1663">
  <properties>
   <property name="type" value="bridge"/>
  </properties>
 </tile>
 <tile id="1664">
  <properties>
   <property name="type" value="bridge"/>
  </properties>
 </tile>
 <tile id="1665">
  <properties>
   <property name="type" value="bridge"/>
  </properties>
 </tile>
 <tile id="1680" terrain="1,1,1,13">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1681" terrain="1,1,13,13">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1682" terrain="1,1,13,1">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1683" terrain="1,13,13,13">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1684" terrain="13,1,13,13">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1686" terrain="13,13,13,13" probability="0.05">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1687" terrain="13,13,13,13" probability="0.05">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1688" terrain="13,13,13,13" probability="0.05">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1689">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1690">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1691">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1692">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1693">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1694">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1695">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1696">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1697">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1698" terrain="14,14,14,14" probability="0.05">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1699" terrain="14,14,14,14" probability="0.05">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1720" terrain="1,13,1,13">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1721" terrain="13,13,13,13">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1722" terrain="13,1,13,1">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1723" terrain="13,13,1,13">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1724" terrain="13,13,13,1">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1726">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="1727">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="1728">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="1729">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="1730">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="1760" terrain="1,13,1,1">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1761" terrain="13,13,1,1">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1762" terrain="13,1,1,1">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1763" terrain="1,13,13,1">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1764" terrain="13,1,1,13">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1766">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="1767">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="1768">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="1769">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="1770">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="1800" terrain="1,1,1,13">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1801">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1802" terrain="1,1,13,1">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1806">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="1807">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="1808">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="1809">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="1810">
  <properties>
   <property name="type" value="plain"/>
  </properties>
 </tile>
 <tile id="1840">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1841">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1842">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1880" terrain="1,13,1,1">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1881">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1882" terrain="13,1,1,1">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1920">
  <properties>
   <property name="type" value="walls"/>
  </properties>
 </tile>
 <tile id="1921">
  <properties>
   <property name="type" value="walls"/>
  </properties>
 </tile>
 <tile id="1922">
  <properties>
   <property name="type" value="walls"/>
  </properties>
 </tile>
 <tile id="1923">
  <properties>
   <property name="type" value="walls"/>
  </properties>
 </tile>
 <tile id="1924">
  <properties>
   <property name="type" value="walls"/>
  </properties>
 </tile>
 <tile id="1925">
  <properties>
   <property name="type" value="walls"/>
  </properties>
 </tile>
 <tile id="1960">
  <properties>
   <property name="type" value="walls"/>
  </properties>
 </tile>
 <tile id="1961">
  <properties>
   <property name="type" value="path"/>
  </properties>
 </tile>
 <tile id="1962">
  <properties>
   <property name="type" value="walls"/>
  </properties>
 </tile>
 <tile id="1963">
  <properties>
   <property name="type" value="walls"/>
  </properties>
 </tile>
 <tile id="1964" terrain=",1,,"/>
 <tile id="1965">
  <properties>
   <property name="type" value="walls"/>
  </properties>
 </tile>
 <tile id="2000">
  <properties>
   <property name="type" value="walls"/>
  </properties>
 </tile>
 <tile id="2001">
  <properties>
   <property name="type" value="walls"/>
  </properties>
 </tile>
 <tile id="2002">
  <properties>
   <property name="type" value="walls"/>
  </properties>
 </tile>
 <tile id="2003">
  <properties>
   <property name="type" value="walls"/>
  </properties>
 </tile>
 <tile id="2004">
  <properties>
   <property name="type" value="walls"/>
  </properties>
 </tile>
 <tile id="2005">
  <properties>
   <property name="type" value="walls"/>
  </properties>
 </tile>
 <tile id="2040">
  <properties>
   <property name="type" value="walls"/>
  </properties>
 </tile>
 <tile id="2041">
  <properties>
   <property name="type" value="walls"/>
  </properties>
 </tile>
 <tile id="2042">
  <properties>
   <property name="type" value="walls"/>
  </properties>
 </tile>
 <tile id="2043">
  <properties>
   <property name="type" value="walls"/>
  </properties>
 </tile>
 <tile id="2044">
  <properties>
   <property name="type" value="walls"/>
  </properties>
 </tile>
 <tile id="2080">
  <properties>
   <property name="type" value="walls"/>
  </properties>
 </tile>
 <tile id="2081">
  <properties>
   <property name="type" value="walls"/>
  </properties>
 </tile>
 <tile id="2082">
  <properties>
   <property name="type" value="walls"/>
  </properties>
 </tile>
 <tile id="2083">
  <properties>
   <property name="type" value="walls"/>
  </properties>
 </tile>
 <tile id="2084">
  <properties>
   <property name="type" value="walls"/>
  </properties>
 </tile>
</tileset>
