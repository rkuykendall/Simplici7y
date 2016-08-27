module VersionsHelper
  def download_button(version)    
    if version.file
      url = ( link_to 'Download', item_download_path(version.item), :class => 'button down' )
    elsif version.link
      url = ( link_to 'Webpage', item_download_path(version.item), :class => 'button next', :target => "_blank" )
    else
      url = ""
    end
    
    '<div class="sidenote">' + url + '</div>'
  end
end
