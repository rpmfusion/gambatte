%define libname_u %{name}
%define libname %{name}-%{version}
%define soname lib%{libname}.so

Name: gambatte
Version: 571
Release: 3%{?dist}
Summary: An accuracy-focused Game Boy / Game Boy Color emulator 

License: GPLv2
URL: http://sourceforge.net/projects/gambatte/
Source0: http://downloads.sourceforge.net/%{name}/%{name}_src-r%{version}.tar.gz
Source1: gambatte-qt.desktop
# Icon made by Peter Verschoor <peterverschoor@xs4all.nl>
Source2: gameboy_icon.png
# Man page made by Anthony J. Bentley <anthony@cathet.us> for OpenBSD
Source3: gambatte_sdl.6
# Andrea Musuruane
# Use system minizip
Patch0: %{name}-537-minizip.patch

BuildRequires: scons
BuildRequires: minizip-devel
BuildRequires: SDL-devel
BuildRequires: qt4-devel
BuildRequires: libXv-devel
BuildRequires: desktop-file-utils
BuildRequires: ImageMagick
Requires: hicolor-icon-theme


%description
Gambatte is an accuracy-focused, open-source, cross-platform
Game Boy Color emulator written in C++. It is based on hundreds of
corner case hardware tests, as well as previous documentation and reverse
engineering efforts.


%package -n libgambatte
Summary: Core emulation code for Gambatte emulator

%description -n libgambatte
Gambatte is an accuracy-focused, open-source, cross-platform
Game Boy Color emulator written in C++. It is based on hundreds of
corner case hardware tests, as well as previous documentation and reverse
engineering efforts.

The core emulation code is contained in a separate library back-end
(libgambatte) written in platform-independent C++. 


%package -n libgambatte-devel
Summary: Development files for libgambatte
Requires: libgambatte = %{version}-%{release}

%description -n libgambatte-devel
This package contains development files for libgambatte.


%package qt
Summary: Qt4 Gambatte front-end

%description qt
Gambatte is an accuracy-focused, open-source, cross-platform
Game Boy Color emulator written in C++. It is based on hundreds of
corner case hardware tests, as well as previous documentation and reverse
engineering efforts.

This is the GUI front-end using Trolltech's Qt4 toolkit.


%package sdl
Summary: SDL Gambatte front-end

%description sdl
Gambatte is an accuracy-focused, open-source, cross-platform
Game Boy Color emulator written in C++. It is based on hundreds of
corner case hardware tests, as well as previous documentation and reverse
engineering efforts.

This is a simple command-line SDL front-end.


%prep
%setup -q -n %{name}_src-r%{version}
%patch0 -p1

# Fix file encoding
for txtfile in README
do
    iconv --from=ISO-8859-1 --to=UTF-8 $txtfile > tmp
    touch -r $txtfile tmp
    mv tmp $txtfile
done

# Fix premissions
find . \( -name *.cpp -o -name *.h \) -exec chmod 644 {} \;

# Use RPM_OPT_FLAGS
sed -i '/QMAKE_CFLAGS/d' gambatte_qt/src/src.pro
sed -i '/QMAKE_CXXFLAGS/d' gambatte_qt/src/src.pro

# Build a dynamic library
sed -i '/^env.Library/i\
env.AppendUnique(SHLINKFLAGS="-Wl,-soname=%{soname}")' libgambatte/SConstruct
sed -i 's/env.Library/env.SharedLibrary/' libgambatte/SConstruct

# Change library name to avoid future collisions with upstream
sed -i "s/'%{libname_u}'/'%{libname}'/" libgambatte/SConstruct
sed -i 's/-l%{libname_u}/-l%{libname}/' gambatte_qt/src/src.pro
sed -i "s/libgambatte.a/%{soname}/" gambatte_sdl/SConstruct


%build
export QMAKE_CFLAGS="%{optflags}"
export QMAKE_CXXFLAGS="%{optflags}"

pushd libgambatte
scons %{?_smp_mflags} CFLAGS="%{optflags}" CXXFLAGS="%{optflags}"
popd

pushd gambatte_sdl
scons %{?_smp_mflags} CFLAGS="%{optflags}" CXXFLAGS="%{optflags}"
popd

pushd gambatte_qt
qmake-qt4 
make %{?_smp_mflags}
popd


%install
# Install include
install -d -m 755 %{buildroot}%{_includedir}/%{name}
install -m 644  libgambatte/include/* %{buildroot}%{_includedir}/%{name}

# Install lib
install -d -m 755 %{buildroot}%{_libdir}
install -m 755 libgambatte/%{soname} %{buildroot}%{_libdir}

# Install bin files
install -d -m 755 %{buildroot}%{_bindir}
install -m 755 gambatte_sdl/gambatte_sdl %{buildroot}%{_bindir}
install -m 755 gambatte_qt/bin/gambatte_qt %{buildroot}%{_bindir}

# Install manpage
mkdir -p %{buildroot}%{_mandir}/man6/
install -p -m 0644 %{SOURCE3} %{buildroot}%{_mandir}/man6/

# Install desktop file
mkdir -p %{buildroot}%{_datadir}/applications
desktop-file-install \
  --dir %{buildroot}%{_datadir}/applications \
  %{SOURCE1}

# Install icons
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/32x32/apps
convert %{SOURCE2} -resize x32 %{buildroot}%{_datadir}/icons/hicolor/32x32/apps/gambatte-qt.png
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/64x64/apps
convert %{SOURCE2} -resize x64 %{buildroot}%{_datadir}/icons/hicolor/64x64/apps/gambatte-qt.png


%post -n libgambatte -p /sbin/ldconfig
%postun -n libgambatte -p /sbin/ldconfig


%post qt
/bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :


%postun qt
if [ $1 -eq 0 ] ; then
    /bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null
    /usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
fi


%posttrans qt
/usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :


%files -n libgambatte
%{_libdir}/%{soname}
%doc changelog COPYING README


%files -n libgambatte-devel
%{_includedir}/%{name}
%doc changelog COPYING README


%files sdl
%{_bindir}/gambatte_sdl
%{_mandir}/man6/gambatte_sdl.6*
%doc changelog COPYING README


%files qt
%{_bindir}/gambatte_qt 
%{_datadir}/icons/hicolor/32x32/apps/gambatte-qt.png
%{_datadir}/icons/hicolor/64x64/apps/gambatte-qt.png
%{_datadir}/applications/gambatte-qt.desktop
%doc changelog COPYING README


%changelog
* Sun Mar 19 2017 RPM Fusion Release Engineering <kwizart@rpmfusion.org> - 571-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Thu Nov 20 2014 Andrea Musuruane <musuruan@gmail.com> - 571-2
- Added manpage by Anthony J. Bentley
- Minor cleanup

* Mon Sep 29 2014 Andrea Musuruane <musuruan@gmail.com> - 571-1
- Updated to upstream r571
- Dropped obsolete Group tags
- Updated icon cache scriptlets

* Thu Sep 11 2014 Sérgio Basto <sergio@serjux.com> - 550-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Fri Dec 20 2013 Andrea Musuruane <musuruan@gmail.com> - 550-1
- Updated to upstream r550
- Dropped cleaning at the beginning of %%install

* Mon Jul 01 2013 Andrea Musuruane <musuruan@gmail.com> - 537-1
- Updated to upstream r537
- Dropped obsolete Group, Buildroot, %%clean and %%defattr

* Sun Mar 03 2013 Nicolas Chauvet <kwizart@gmail.com> - 0.4.1-7
- Mass rebuilt for Fedora 19 Features

* Sat Mar 17 2012 Andrea Musuruane <musuruan@gmail.com> - 0.4.1-6
- Added a patch to link against libX11
- Fixed Source0 URL

* Fri Mar 02 2012 Nicolas Chauvet <kwizart@gmail.com> - 0.4.1-5
- Rebuilt for c++ ABI breakage

* Wed Feb 08 2012 Nicolas Chauvet <kwizart@gmail.com> - 0.4.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Sat Apr 04 2009 Andrea Musuruane <musuruan@gmail.com> - 0.4.1-3
- Added a patch to fix gcc 4.4 errors

* Sun Mar 29 2009 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 0.4.1-2
- rebuild for new F11 features

* Sat Jan 31 2009 Andrea Musuruane <musuruan@gmail.com> - 0.4.1-1
- Updated to upstream 0.4.1
- Changed back to qt4-devel from qt-devel in BR
- Changed descriptions to match the one upstream uses
- Dropped alsa patch, applied upstream
- Changed libname to avoid future collisions with upstream

* Tue Dec 02 2008 Andrea Musuruane <musuruan@gmail.com> - 0.4.0-4
- Changed qt4-devel to qt-devel in BR
- Added a patch to compile alsa under linux 64bit systems

* Wed Nov 26 2008 Andrea Musuruane <musuruan@gmail.com> - 0.4.0-3
- Used an icon made by Peter Verschoor
- Cosmetic changes

* Tue Nov 25 2008 Andrea Musuruane <musuruan@gmail.com> - 0.4.0-2
- Improved macro usage
- Preserved timestamp of doc files converted to UTF-8
- Cosmetic changes

* Sat Nov 15 2008 Andrea Musuruane <musuruan@gmail.com> - 0.4.0-1
- First release for RPM Fusion
- Made a patch to use rpm optflags
- Made a patch to use system libraries

