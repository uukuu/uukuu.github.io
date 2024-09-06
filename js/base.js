function aside_left_profile()
{
    document.getElementById("aside-btn-profile").style.borderBottom="1px solid #ebf0fa";
    document.getElementById("aside-btn-tool").style.borderBottom="none";
    document.getElementById("aside-profile").style.display="block";
    document.getElementById("aside-tool").style.display="none";
}
function aside_left_tool()
{
    document.getElementById("aside-btn-tool").style.borderBottom="1px solid #ebf0fa";
    document.getElementById("aside-btn-profile").style.borderBottom="none";
    document.getElementById("aside-profile").style.display="none";
    document.getElementById("aside-tool").style.display="block";
}


function aside_left_profile2()
{
    document.getElementById("aside-btn-profile2").style.borderBottom="1px solid #ebf0fa";
    document.getElementById("aside-profile2").style.display="block";
    document.getElementById("aside-btn-tool2").style.borderBottom="none";
    document.getElementById("aside-tool2").style.display="none";
    document.getElementById("aside-btn-menu2").style.borderBottom="none";
    document.getElementById("aside-menu2").style.display="none";
    document.getElementById("aside-menu2").style.overflowY="hidden";
}
function aside_left_tool2()
{
    document.getElementById("aside-btn-tool2").style.borderBottom="1px solid #ebf0fa";
    document.getElementById("aside-tool2").style.display="block";
    document.getElementById("aside-btn-profile2").style.borderBottom="none";
    document.getElementById("aside-profile2").style.display="none";
    document.getElementById("aside-btn-menu2").style.borderBottom="none";
    document.getElementById("aside-menu2").style.display="none";
    document.getElementById("aside-menu2").style.overflowY="hidden";
}
function aside_left_menu2()
{
    document.getElementById("aside-btn-menu2").style.borderBottom="1px solid #ebf0fa";
    document.getElementById("aside-menu2").style.display="block";
    document.getElementById("aside-menu2").style.overflowY="auto";
    document.getElementById("aside-btn-profile2").style.borderBottom="none";
    document.getElementById("aside-profile2").style.display="none";
    document.getElementById("aside-btn-tool2").style.borderBottom="none";
    document.getElementById("aside-tool2").style.display="none";

}

function get_height()
{
    var H=document.getElementById("mainpart").clientHeight;
    H=Math.max(H,500);
    H+="px";
    document.getElementById("mainuuku").style.height="calc("+H+" + 100vh - 20px)";
    setTimeout(function(){
        H=document.getElementById("mainpart").clientHeight;
        H=Math.max(H,500);
        H+="px";
        document.getElementById("mainuuku").style.height="calc("+H+" + 100vh - 20px)";

    }, 260);
}

// function get_background()
// {
//     var H=window.innerHeight;
//     console.log(H)
//     H+="px";
//     var back_img=document.getElementById("background-image");
//     if(back_img.style.height<=H)
//     {
//         back_img.style.height=H;
//     }
// }