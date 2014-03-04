function XSILoadPlugin( in_reg )
{
	in_reg.Author = 'junki';
	in_reg.Name = 'Capchan3';
	in_reg.Email = 'junkithejunkie@gmail.com';
	in_reg.URL = 'http://junkithejunkie.cocolog-nifty.com/';
	in_reg.Major = 1;
	in_reg.Minor = 0;

	in_reg.RegisterCommand('Capchan3','Capchan3');
	in_reg.RegisterCommand('CapchanSelected','CapchanSelected');
	//RegistrationInsertionPoint - do not remove this line

	return true;
}

function XSIUnloadPlugin( in_reg )
{
	var strPluginName;
	strPluginName = in_reg.Name;
	Application.LogMessage(strPluginName + ' has been unloaded.',siVerbose);
	return true;
}

function Capchan3_Init( in_ctxt )
{
	var oCmd;
	oCmd = in_ctxt.Source;
	oCmd.Description = 'aaa';
	oCmd.Tooltip = 'bbb';
	oCmd.ReturnValue = true;

	var oArgs;
	oArgs = oCmd.Arguments;

	oArgs.Add('RootFolder',siArgumentInput,ActiveProject.Path);
	oArgs.Add('Prefix',siArgumentInput,'');
	oArgs.Add('FileName',siArgumentInput,'CapchanSeq');
	oArgs.Add('FileFormat',siArgumentInput,'.pic');
	oArgs.Add('PresetFile',siArgumentInput,'');
	oArgs.Add('PresetType',siArgumentInput,'');
	
	oArgs.Add('IsCreateFolder',siArgumentInput,true);
	
	oArgs.Add('StartFrame',siArgumentInput,1);
	oArgs.Add('EndFrame',siArgumentInput,24);
	oArgs.Add('Step',siArgumentInput,1);
	oArgs.Add('FPS',siArgumentInput,24);
	
	oArgs.Add('View',siArgumentInput,'B');
	oArgs.Add('Aspect',siArgumentInput,1.778);
	oArgs.Add('Xres',siArgumentInput,864);
	oArgs.Add('Yres',siArgumentInput,486);

	oArgs.Add('BGColor',siArgumentInput,1);
	oArgs.Add('IsAudio',siArgumentInput,false);
	oArgs.Add('Player',siArgumentInput,'Flipbook');
	oArgs.Add('CustomPlayer',siArgumentInput,'');
	oArgs.Add('OGLAA',siArgumentInput,false);
	oArgs.Add('ClearSelection',siArgumentInput,true);
	oArgs.Add('Roto',siArgumentInput,2);
	
	//oArgs.Add('xxx',siArgumentInput,'');	
	
	return true;
}

function Capchan3_Execute(	RootFolder,Prefix,FileName,FileFormat,PresetFile,PresetType,
							IsCreateFolder,
							StartFrame,EndFrame,Step,FPS,
							View,Aspect,Xres,Yres,
							BGColor,IsAudio,Player,CustomPlayer,OGLAA,ClearSelection,Roto
							)
{
	Err = false;
	var oFSO = new ActiveXObject( 'Scripting.FileSystemObject' ) ;
	if (!oFSO.FolderExists(RootFolder))
	{
		Logmessage('そんな Root Folder はねえよ',siError);
		Err = true;
	}
	else if (FileFormat ==  '.mov' || FileFormat ==  '.avi' )
	{
		if (!oFSO.FileExists(PresetFile))
		{
			Logmessage('そんな Preset File はねえよ',siError);
			Err = true;
		}
	}
	if (Err == false)
	{
		GoCapchan3(	RootFolder,Prefix,FileName,FileFormat,PresetFile,PresetType,
					IsCreateFolder,
					StartFrame,EndFrame,Step,FPS,
					View,Aspect,Xres,Yres,
					BGColor,IsAudio,Player,CustomPlayer,OGLAA,ClearSelection,Roto
					);
	}
	return true;
}
function GoCapchan3(	RootFolder,Prefix,FileName,FileFormat,PresetFile,PresetType,
						IsCreateFolder,
						StartFrame,EndFrame,Step,FPS,
						View,Aspect,Xres,Yres,
						BGColor,IsAudio,Player,CustomPlayer,OGLAA,ClearSelection,Roto
						)
{
	var oVC = Dictionary.GetObject('ViewportCapture');
	var oPC = Dictionary.GetObject('PlayControl');
	
	Yres = Math.round(Xres / Aspect);
	FileName = Prefix + FileName;

	if (IsCreateFolder == true)
	{
		FolderPath = RootFolder + '\\' + FileName;
		CreateFolder(FolderPath);
	}
	else
	{
		FolderPath = RootFolder;
	}
	
	if (FileFormat ==  '.mov' || FileFormat ==  '.avi' )
	{//	Movie File Specific
		bMovie = true;
		SetVC(oVC,'Movie',true);
		LoadPreset(PresetFile,oVC);		
		FilePath = FolderPath + '\\' + FileName + FileFormat;
		SetVC(oVC,'File Name',FilePath);
		if (Player == 'NativePlayer')
		{
			SetVC(oVC,'Launch Flipbook',true );
			SetVC(oVC,'Use Native Movie Player',true);
		}
		else
		{
			SetVC(oVC,'Launch Flipbook',false );
			SetVC(oVC,'Use Native Movie Player',false);
		}
	}
	else
	{//	Sequence File Specific
		bMovie = false;
		FilePath = FolderPath + '\\' + FileName + '_' + FileFormat;
		
		SetVC(oVC,'File Name',FilePath);
		SetVC(oVC,'Launch Flipbook',false);//独自 Flipbook を起動するためシステム側はオフ
		
		//	Store the file path of 1st frame in the sequence
		StartFrameString = StartFrame + '';
		if (StartFrameString.length == 1)
		{
			StartFrameString = '000' + StartFrameString;
		}
		else if (StartFrameString.length == 2)
		{
			StartFrameString = '00' + StartFrameString;
		}
		else if (StartFrameString.length == 3)
		{
			StartFrameString = '0' + StartFrameString;
		}
		FirstFrameFilePath = FolderPath + '\\' + FileName + '_' + StartFrameString + FileFormat;
	}

	//	Common
	SetVC(oVC,'Start Frame',StartFrame);
	SetVC(oVC,'End Frame',EndFrame);
	
	SetVC(oVC,'Width',Xres);
	SetVC(oVC,'Height',Yres);
	SetVC(oVC,'Frame Rate',FPS);
	SetVC(oVC,'Record Audio Track',IsAudio);
	if (OGLAA == true)
	{
		SetVC(oVC,'OpenGL Anti-Aliasing',4);
	}
	else
	{
		SetVC(oVC,'OpenGL Anti-Aliasing',1);
	}
	SetVC(oVC,'Padding','(fn)####(ext)');

	//	Step
	OriginalStep = oPC.Step.value;
	oPC.Step.value = Step;
	
	//	Selection Clear
	if (ClearSelection == true)
	{
		var OriginalSelCol = XSIFactory.CreateObject('XSI.Collection');
		OriginalSelCol.AddItems(Selection);
		Selection.Clear();
	}
	//	BG Color
	var oColors = ActiveProject.ActiveScene.Colors;
	OriginalBGColor = oColors.Parameters('backgroundcol').value;
	if (BGColor != 2)
	{
		oColors.Parameters('backgroundcol').value = BGColor;
	}
	
	//	Get Camera
	FocusedViewNum = GetViewportNumberFromString(View);
	var oCam = GetViewCamera(FocusedViewNum); //		GetViewCamera command expects a number between 0-3.
	var oCamvis = oCam.Properties("Camera Visibility");
	var oCamdisp = oCam.Properties("Camera Display");	

	//	Rotoscope
	RotoFlag = false;
	if (Roto != 2)
	{
		OriginalRoto = oCamdisp.rotoenable.value;
		oCamdisp.rotoenable.value = Roto;
		RotoFlag = true;
	}

	//	Camera Visibility
	HideNameFlag = false;
	HideObjFlag = false;
	HideInfoFlag = false;
	var oCapchan3 = GetItem('*.*Capchan3Options*')(0);
	if (oCapchan3 != null)
	{
		if (oCapchan3.bHideName.value)
		{
			if ( oCapchan3.sHideName.value == '')
			{
				HideName = 'CapchanHiddenGroup';
			}
			else
			{
				HideName = oCapchan3.sHideName.value;
			}
			var HideObjects = XSIFactory.CreateObject('XSI.Collection');
			HideObjects.unique = true;
			HideObjects = GetItem('*' + HideName + '*');
			var ViewvisValueArray = new Array();
			for (i=0; i<HideObjects.count; i++)
			{
				ViewvisValueArray[i] = HideObjects(i).viewvis.value;
				SetValue(HideObjects(i) + ".viewvis", 0, null);
			}
			HideNameFlag = true;
		}
		if (oCapchan3.bHideObj.value)
		{
			//	Store 
			objnurbssrf = oCamvis.objnurbssrf.value;
			objpolymesh = oCamvis.objpolymesh.value;
			objinstances = oCamvis.objinstances.value;
			objparticles = oCamvis.objparticles.value;
			objcurves = oCamvis.objcurves.value;
			objhair = oCamvis.objhair.value;
			objnulls = oCamvis.objnulls.value;
			objcameras = oCamvis.objcameras.value;
			objimpgeometry = oCamvis.objimpgeometry.value;
			objlights = oCamvis.objlights.value;
			objctrlother = oCamvis.objctrlother.value;
			objctrltransfogroups = oCamvis.objctrltransfogroups.value;
			objctrlchnroots = oCamvis.objctrlchnroots.value;
			objctrlchnjnts = oCamvis.objctrlchnjnts.value;
			objctrlchneff = oCamvis.objctrlchneff.value;
			objctrllattices = oCamvis.objctrllattices.value;
			objctrlwaves = oCamvis.objctrlwaves.value;
			objctrltextsupp = oCamvis.objctrltextsupp.value;
			
			//	Change
			oCamvis.objnurbssrf.value = oCapchan3.objnurbssrf.value;
			oCamvis.objpolymesh.value = oCapchan3.objpolymesh.value;
			oCamvis.objinstances.value = oCapchan3.objinstances.value;
			oCamvis.objparticles.value = oCapchan3.objparticles.value;
			oCamvis.objcurves.value = oCapchan3.objcurves.value;
			oCamvis.objhair.value = oCapchan3.objhair.value;
			oCamvis.objnulls.value = oCapchan3.objnulls.value;
			oCamvis.objcameras.value = oCapchan3.objcameras.value;
			oCamvis.objimpgeometry.value = oCapchan3.objimpgeometry.value;
			oCamvis.objlights.value = oCapchan3.objlights.value;
			oCamvis.objctrlother.value = oCapchan3.objctrlother.value;
			oCamvis.objctrltransfogroups.value = oCapchan3.objctrltransfogroups.value;
			oCamvis.objctrlchnroots.value = oCapchan3.objctrlchnroots.value;
			oCamvis.objctrlchnjnts.value = oCapchan3.objctrlchnjnts.value;
			oCamvis.objctrlchneff.value = oCapchan3.objctrlchneff.value;
			oCamvis.objctrllattices.value = oCapchan3.objctrllattices.value;
			oCamvis.objctrlwaves.value = oCapchan3.objctrlwaves.value;
			oCamvis.objctrltextsupp.value = oCapchan3.objctrltextsupp.value;
			
			HideObjFlag = true;
		}
		if (oCapchan3.bHideInfo.value)
		{
			//	Store 
			gridvis = oCamvis.gridvis.value;
			gridaxisvis = oCamvis.gridaxisvis.value;
			gridrulervis = oCamvis.gridrulervis.value;
			gridfieldguidevis = oCamvis.gridfieldguidevis.value;
			
			
			refreshrate = oCamvis.refreshrate.value;
			vsyncinfo = oCamvis.vsyncinfo.value;
			currenttime = oCamvis.currenttime.value;
			fastplaybackcache = oCamvis.fastplaybackcache.value;
			selectioninfo = oCamvis.selectioninfo.value;
			sceneinfo = oCamvis.sceneinfo.value;
			constructionlevel = oCamvis.constructionlevel.value;
			simulationinfo = oCamvis.simulationinfo.value;
			custominfo = oCamvis.custominfo.value;
			transforminfo = oCamvis.transforminfo.value;
			custominfoproxynames = oCamvis.custominfoproxynames.value;
			
			//	Change
			oCamvis.gridvis.value = oCapchan3.gridvis.value;
			oCamvis.gridaxisvis.value = oCapchan3.gridaxisvis.value;
			oCamvis.gridrulervis.value = oCapchan3.gridrulervis.value;
			oCamvis.gridfieldguidevis.value = oCapchan3.gridfieldguidevis.value;
			
			oCamvis.refreshrate.value = oCapchan3.refreshrate.value;
			oCamvis.vsyncinfo.value = oCapchan3.vsyncinfo.value;
			oCamvis.currenttime.value = oCapchan3.currenttime.value;
			oCamvis.fastplaybackcache.value = oCapchan3.fastplaybackcache.value;
			oCamvis.selectioninfo.value = oCapchan3.selectioninfo.value;
			oCamvis.sceneinfo.value = oCapchan3.sceneinfo.value;
			oCamvis.constructionlevel.value = oCapchan3.constructionlevel.value;
			oCamvis.simulationinfo.value = oCapchan3.simulationinfo.value;
			oCamvis.custominfo.value = oCapchan3.custominfo.value;
			oCamvis.transforminfo.value = oCapchan3.transforminfo.value;
			oCamvis.custominfoproxynames.value = oCapchan3.custominfoproxynames.value;
			
			HideInfoFlag = true;
		}
	}	
	
	////
	////	Start
	ViewNum = GetViewportNumberFromString(View) + 1;
	CaptureViewport(ViewNum,false);
	////
	////
	
	
	////	Playback
	
	if (bMovie == true)
	{
		FlipOption = FilePath;
	}
	else
	{
		FlipOption = 	'-p ' + '(fn)####(ext)' + ' -s ' + FilePath + ' ' +
						StartFrame + ' ' + EndFrame + ' ' + Step + ' ' + FPS;
	}	
	
	
	if (Player == 'Flipbook')
	{
		Flipbook(FlipOption);
	}
	else if (Player == 'CustomPlayer')
	{		
		var oFSO = new ActiveXObject( 'Scripting.FileSystemObject' ) ;
		try
		{
			if (bMovie == true)
			{
				XSIUtils.LaunchProcess(CustomPlayer + ' ' + FlipOption);
			}
			else
			{
				XSIUtils.LaunchProcess(CustomPlayer + ' ' + FirstFrameFilePath);
			}
		}
		catch(e)
		{
			Logmessage('[ キャプちゃん!! ver3.0 ] カスタムプレイヤがなんかおかしいから Flipbook で再生してやるよ。',siWarning);
			Flipbook(FlipOption);
		}	
	}
	else if (Player == 'NativePlayer' && bMovie == false)	//	NativePlayer が選択されているにも関わらず Movie フォーマットでない場合（Native は Movie フォーマットのみだから）
	{
		Flipbook(FlipOption);
	}
	
/* 	if (bMovie == false)
	{
		FlipOption = 	'-p ' + '(fn)####(ext)' + ' -s ' + FilePath + ' ' +
						StartFrame + ' ' + EndFrame + ' ' + Step + ' ' + FPS;
	}
	else 
	{
		FlipOption = FilePath;
	}
	if (Player == 'Flipbook' || (Player == 'NativePlayer' && bMovie == false))
	{
		Flipbook(FlipOption);
	}
	else if (Player == 'CustomPlayer' && bMovie == true)
	{
		var oFSO = new ActiveXObject( 'Scripting.FileSystemObject' ) ;
		if (!oFSO.FolderExists(CustomPlayer))
		{
			try
			{
				XSIUtils.LaunchProcess(CustomPlayer + ' ' + FlipOption);
			}
			catch(e)
			{
				Logmessage('[ キャプちゃん!! ver3.0 ] カスタムプレイヤがなんかおかしいから Flipbook で再生してやるよ。',siWarning);
				Flipbook(FlipOption);
			}
		}
		else
		{
			Logmessage('[ キャプちゃん!! ver3.0 ] カスタムプレイヤが見つからねえから Flipbook で再生してやるよ。',siWarning);
			Flipbook(FlipOption);
		}
	} */
	
	
	
	////	Save option to PPG
	if (oCapchan3 != null)
	{
		oCapchan3.sLastFlipbook.value = FlipOption;
	}

	////	Restore
	
	//	Rotoscope
	if (RotoFlag == true)
	{
		oCamdisp.rotoenable.value = OriginalRoto;
	}
	
	//	Camera Visibility
	if (HideNameFlag == true)
	{
		for (i=0; i<HideObjects.count; i++)
		{
			HideObjects(i).viewvis.value = ViewvisValueArray[i];
		}
	}
	if (HideObjFlag == true)
	{
		oCamvis.objnurbssrf.value = objnurbssrf;
		oCamvis.objpolymesh.value = objpolymesh;
		oCamvis.objinstances.value = objinstances;
		oCamvis.objparticles.value = objparticles;
		oCamvis.objcurves.value = objcurves;
		oCamvis.objhair.value = objhair;
		oCamvis.objnulls.value = objnulls;
		oCamvis.objcameras.value = objcameras;
		oCamvis.objimpgeometry.value = objimpgeometry;
		oCamvis.objlights.value = objlights;
		oCamvis.objctrlother.value = objctrlother;
		oCamvis.objctrltransfogroups.value = objctrltransfogroups;
		oCamvis.objctrlchnroots.value = objctrlchnroots;
		oCamvis.objctrlchnjnts.value = objctrlchnjnts;
		oCamvis.objctrlchneff.value = objctrlchneff;
		oCamvis.objctrllattices.value = objctrllattices;
		oCamvis.objctrlwaves.value = objctrlwaves;
		oCamvis.objctrltextsupp.value = objctrltextsupp;
	}
	if (HideInfoFlag == true)
	{		
		oCamvis.gridvis.value = gridvis;
		oCamvis.gridaxisvis.value = gridaxisvis;
		oCamvis.gridrulervis.value = gridrulervis;
		oCamvis.gridfieldguidevis.value = gridfieldguidevis;
		
		oCamvis.refreshrate.value = refreshrate;
		oCamvis.vsyncinfo.value = vsyncinfo;
		oCamvis.currenttime.value = currenttime;
		oCamvis.fastplaybackcache.value = fastplaybackcache;
		oCamvis.selectioninfo.value = selectioninfo;
		oCamvis.sceneinfo.value = sceneinfo;
		oCamvis.constructionlevel.value = constructionlevel;
		oCamvis.simulationinfo.value = simulationinfo;
		oCamvis.custominfo.value = custominfo;
		oCamvis.transforminfo.value = transforminfo;
		oCamvis.custominfoproxynames.value = custominfoproxynames;	
	}
	
	//	BG Color	
	oColors.Parameters('backgroundcol').value = OriginalBGColor;
	
	//	Step
	oPC.Step.value = OriginalStep;
	
	//	Selection
	SelectObj(OriginalSelCol);

}

var CheckCapchan3Options = function()
{
    var oCapchan3 = GetItem('*.*Capchan3Options*')(0);
    if (oCapchan3 == null)
    {
        var oCapchan3 = ActiveSceneRoot.AddProperty('Capchan3Options');

    }
    return oCapchan3;
}
function CapchanSelected_Init( in_ctxt )
{
	var oCmd;
	oCmd = in_ctxt.Source;
	oCmd.Description = 'aaa';
	oCmd.Tooltip = 'bbb';
	oCmd.ReturnValue = true;

	//var oArgs;
	//oArgs = oCmd.Arguments;
	//oArgs.Add('OptionProp', siArgumentInput);
	return true;
}

function CapchanSelected_Execute()
{
    /* 選択オブジェクト以外全部非表示にしてキャプチャとる。おわったら戻す */

    //	*******************************************
    //if (OptionProp == null)
    if ( true )
    {
        OptionProp = CheckCapchan3Options();
    }
    //	*******************************************

	RootFolder = OptionProp.sRootFolder.value;
	Prefix = OptionProp.sPrefix.value;
	FileName = OptionProp.sFileName.value;
	FileFormat = OptionProp.sFileFormat.value;
	PresetFile = OptionProp.sPresetFile.value;
	PresetType = OptionProp.sPresetType.value;
	IsCreateFolder = OptionProp.bCreateFolder.value;
	StartFrame = OptionProp.iStartFrame.value;
	EndFrame = OptionProp.iEndFrame.value;
	Step = OptionProp.iStep.value;
	FPS = OptionProp.dFPS.value;
	View = OptionProp.sViewport.value;
	Aspect = OptionProp.dAspect.value;
	Xres = OptionProp.iXres.value;
	Yres = OptionProp.iYres.value;
	BGColor = OptionProp.iBGColor.value;
	IsAudio = OptionProp.bAudio.value;
	Player = OptionProp.sPlayer.value;
	CustomPlayer = OptionProp.sCustomPlayer.value;
	OGLAA = OptionProp.bOGLAA.value;
	ClearSelection = OptionProp.bSelectionClear.value;
	Roto = OptionProp.iRoto.value;

    ////////////////////////    
    // store selection and all visibility
    var store_vis = {};
    all = ActiveSceneRoot.FindChildren("*", "","", true);
    for (i=0; i<all.Count; i++)
    {
        var x = all.Item(i);
        if (x == null){ continue; }
        if (x.Name == "Scene_Root" ){ continue; }
        store_vis[x.ObjectID] = x.Properties("visibility").viewvis.Value;
        x.Properties("visibility").viewvis.Value = false;
    }

    try {
        for (i=0; i<Selection.Count; i++)
        {
            var o = Selection.Item(i);
            if ( o.Properties == null ) { continue; }
            try {
                o.Properties("visibility").viewvis.Value = true;
            } catch {
                LogMessage( "skip setting visibility " + o.FullName );
            }
        }

        // take capture
        Capchan3(	RootFolder,Prefix,FileName,FileFormat,PresetFile,PresetType,
                    IsCreateFolder,
                    StartFrame,EndFrame,Step,FPS,
                    View,Aspect,Xres,Yres,
                    BGColor,IsAudio,Player,CustomPlayer,OGLAA,ClearSelection,Roto);
    } finally {
        // restore visibility
        for (var k in store_vis)
        {
            if (store_vis.hasOwnProperty(k))
            {
                GetObjectFromID(k).Properties("visibility").viewvis.Value = store_vis[k];
            }
        }
    }
}


function SetVC(oVC,in_param, in_value)
{
	oVC.NestedObjects.item(in_param).value = in_value;
}
function CreateFolder(in_FolderPath)
{
	var oFSO = new ActiveXObject( 'Scripting.FileSystemObject' ) ;
	if (!oFSO.FolderExists(in_FolderPath))
	{
		var folder = oFSO.CreateFolder(in_FolderPath );
	}
}
function SetVCParam(oVC,in_param, in_value)
{
	oVC.NestedObjects.item(in_param).value = in_value;
}
function GetItem( in_Str )
{ 
	var oColl = XSIFactory.CreateObject( 'XSI.Collection' );
	oColl.items = in_Str;
	return oColl;
}
function GetViewportNumberFromString(in_Str)
{
	switch(in_Str)
	{
		case 'A': ViewportNumber = 0;
			break;
		case 'B': ViewportNumber = 1;
			break;
		case 'C': ViewportNumber = 2;
			break;
		case 'D': ViewportNumber = 3;
			break;
     }
	 return ViewportNumber;
}
