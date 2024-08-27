# 工具类
import os

from pbxproj import XcodeProject
from pbxproj import PBXGroup
from pbxproj import PBXBuildFile
# from pbxproj.pbxextensions.ProjectFiles import ProjectFiles
from pbxproj.pbxextensions.ProjectFiles import *


from pbxproj import PBXFileReference

class CodeUtils:

    # 遍历某一目录下，获取文件通过闭包传递回去
    def enumFileInDir(self, path, block,extensions:[], prefix:str="", recursive:bool=False, blackPaths:[]=[]):
        if recursive == False:
            if blackPaths.__contains__(path) == True:
                return True
            list = self.listFileInDir(path, prefix=prefix)
            for file in list:
                isTaregetExtension = False
                for extension in extensions:
                    if file.endswith(extension) == True:
                        isTaregetExtension = True
                        break
                if isTaregetExtension == False:
                    continue
                filePath = os.path.join(path, file)
                result = block(filePath)
                if result == False:
                    print("enumFileInDir failed: ",filePath)
                    return False
            return True
        else:
            if blackPaths.__contains__(path) == True:
                return True
            fileList = self.listFileInDir(path, prefix=prefix)
            for file in fileList:
                isTaregetExtension = False
                for extension in extensions:
                    if file.endswith(extension) == True:
                        isTaregetExtension = True
                        break
                if isTaregetExtension == False:
                    continue
                filePath = os.path.join(path, file)
                result = block(filePath)
                if result == False:
                    print("enumFileInDir failed: ", filePath)
                    return False
            folderList = self.listFolderInDir(path)
            if len(folderList) > 0:
                for folder in folderList:
                    subPath = os.path.join(path, folder)
                    result = self.enumFileInDir(subPath, block, extensions, prefix, recursive, blackPaths)
                    if result == False:
                        return False
            return True

    # 获取某一目录下的文件夹列表
    def listFolderInDir(self, path, prefix:str=""):
        list = []
        for file in os.listdir(path):
            file_path = os.path.join(path, file)
            if os.path.isdir(file_path):
                if len(prefix) != 0:
                    if file.startswith(prefix):
                        list.append(file)
                else:
                    list.append(file)
        return list

    # 获取某一目录下的文件列表
    def listFileInDir(self, path, prefix:str=""):
        list = []
        for file in os.listdir(path):
            file_path = os.path.join(path, file)
            if os.path.isdir(file_path) == False:
                # print("文件：" + file)
                if len(prefix) != 0:
                    if file.startswith(prefix):
                        list.append(file)
                else:
                    list.append(file)
        return list

    def addFolderReferenceToXcode(self, project:XcodeProject, foler:str, path:str, parentGroup:PBXGroup, target_name:str=""):
        # results = project.add_folder(path=path, create_groups=True, recursive=False, parent=parentGroup,
        #                                   target_name=target_name)
        if not os.path.isdir(path):
            return False
        result = project.get_or_create_group(name=foler,path=path,parent=parentGroup)
        if result == None:
            print("添加xcode文件夹引用失败,results == None，path：",path)
            return False
        return True

    def addFileReferenceToXcode(self, project:XcodeProject, path:str, parentGroup:PBXGroup, target_name:str=""):
        # print("addFileReferenceToXcode:",path)
        # results = project.add_file(path=path,parent=parentGroup,target_name=target_name, force=False)
        force = False
        file_options = FileOptions()
        parent = parentGroup
        tree = TreeType.SOURCE_ROOT
        results = []
        # if it's not forced to add the file stop if the file already exists.
        if not force:
            target_name = self._filter_targets_without_path(project, path, target_name)
            if target_name.__len__() == 0:
                return []

        file_ref, abs_path, path, tree, expected_build_phase = project._add_file_reference(path, parent, tree, force,
                                                                                        file_options)
        if path is None or tree is None:
            return None

        # no need to create the build_files, done
        if not file_options.create_build_files:
            return results

        # create build_files for the targets
        results.extend(project._create_build_files(file_ref, target_name, expected_build_phase, file_options))

        # special case for the frameworks and libraries to update the search paths
        if abs_path is None:
            return results

        # the path is absolute and it's outside the scope of the project for linking purposes
        library_path = os.path.join('$(SRCROOT)', os.path.split(file_ref.path)[0])
        if os.path.isfile(abs_path):
            project.add_library_search_paths([library_path], recursive=False, escape=" " in library_path)
        else:
            project.add_framework_search_paths([library_path, '$(inherited)'], recursive=False, escape=" " in library_path)

        if results == None:
            print("添加xcode文件引用失败,results == None，path：", path)
            return False
        # if len(results) == 0:
        #     print("添加xcode文件引用失败,len(results) == 0，path：", path)
        #     return False
        if results.__contains__(None):
            print("添加xcode文件引用失败,results.__contains__(None)，path：", path)
            return False
        return True

    # 移除文件在Xcode中的引用
    def removeFileReferenceFromXcode(self, project:XcodeProject, file_ref:PBXFileReference, target_name:str=None):
        if file_ref is None:
            return False

        for target, build_phase in project.objects.get_buildphases_on_target(target_name):

            for build_file_id in filter(lambda x: x in project.objects, build_phase.files):
                build_file = project.objects[build_file_id]
                if 'fileRef' not in build_file:
                    continue
                if build_file.fileRef == file_ref.get_id():
                    # remove the build file from the phase
                    build_phase.remove_build_file(build_file)

            # if the build_phase is empty remove it too, unless it's a shell script.
            if build_phase.files.__len__() == 0 and build_phase.isa != 'PBXShellScriptBuildPhase':
                # remove the build phase from the target
                target.remove_build_phase(build_phase)

        # remove it if it's removed from all targets or no build file reference it
        if len([1 for x in project.objects.get_objects_in_section('PBXBuildFile') if 'fileRef' in x and x.fileRef == file_ref.get_id()]) != 0:
            return True

        # remove the file from any groups if there is no reference from any target
        for group in filter(lambda x: file_ref.get_id() in x.children, project.objects.get_objects_in_section('PBXGroup')):
            group.remove_child(file_ref)

        # the file is not referenced in any build file, remove it
        del project.objects[file_ref.get_id()]
        return True
    # 移除文件夹group在Xcode中的引用
    def removeGroupFromXcode(self, project:XcodeProject, group:PBXGroup, recursive=True):
        """
                Remove the group matching the given group_id. If recursive is True, all descendants of this group are also removed.
                :param group_id: The group id to be removed
                :param recursive: All descendants should be removed as well
                :return: True if the element was removed successfully, False if an error occured or there was nothing to remove.
                """
        if group is None:
            return False

        result = True
        # iterate over the children and determine if they are file/group and call the right method.
        for subgroup_id in list(group.children):
            subgroup = project.objects[subgroup_id]
            if subgroup is None:
                return False

            if recursive and isinstance(subgroup, PBXGroup):
                result &= self.removeGroupFromXcode(project=project,group=subgroup, recursive=recursive)
            if isinstance(subgroup, PBXFileReference):
                file_ref:PBXFileReference = subgroup
                result &= self.removeFileReferenceFromXcode(project=project,file_ref=file_ref)

        if not result:
            return False

        del project.objects[group.get_id()]

        # remove the reference from any other group object that could be containing it.
        for other_group in project.objects.get_objects_in_section('PBXGroup'):
            other_group.remove_child(group)

        return True

        # 获取相对路径

    def getRelativePath(self, parentPath: str, path: str):
        return path.removeprefix(parentPath)

    # 获取某一路径下的文件名字
    def getFileName(self, path:str):
        components = path.split("/")
        count = len(components)
        if count == 0:
            return ""
        lastIndex = count - 1
        fileName = components[lastIndex]
        return fileName



# 从groups中获取指定名字的group
    def findGroup(self, project:XcodeProject, groupName:str, parentGroup:PBXGroup):
        groups = project.get_groups_by_name(name=groupName, parent=parentGroup)
        for group in groups:
            if group.get_name() == groupName:
                return group
        return None

    # 获取根group
    def getRootGroup(self, project:XcodeProject, rootCodePath:str):
        rootGroupName = self.getRootGroupName(rootCodePath=rootCodePath)
        parentGroups = project.get_groups_by_path(path=rootGroupName)
        for group in parentGroups:
            if group.get_name() == rootGroupName:
                return group
        return None

    # 获取根group的名字
    def getRootGroupName(self, rootCodePath:str):
        components = rootCodePath.split("/")
        count = len(components)
        if count == 0:
            return None
        lastIndex = count - 1
        rootGroupName = components[lastIndex]
        return  rootGroupName

    def getFileNameAt(self, path:str):
        if os.path.isfile(path) == False:
            return None
        components = path.split("/")
        count = len(components)
        if count == 0:
            return None
        lastIndex = count - 1
        fileName = components[lastIndex]
        return fileName


    def getParentGroupName(self,path:str):
        components = path.split("/")
        count = len(components)
        if count == 0:
            return None
        lastIndex = count - 1
        parentGroupName = components[lastIndex]
        return parentGroupName


    # 在某个group下根据fileName查找文件
    def findFileAt(self, project:XcodeProject, fileName:str, parentGroup:PBXGroup):
        files = project.get_files_by_name(name=fileName, parent=parentGroup)
        for file in files:
            if file.get_name() == fileName:
                return file
        return None

    # 判断文件在某个target中是否存在
    def isFileExists(self, project:XcodeProject, path, target_name):
        potential_targets = project.objects.get_targets(target_name)
        for target in potential_targets.copy():
            for build_phase_id in target.buildPhases:
                build_phase = project.get_object(build_phase_id)
                for build_file_id in build_phase.files:
                    build_file = project.get_object(build_file_id)
                    if build_file is None:
                        continue
                    if 'fileRef' not in build_file:
                        continue
                    file_ref = project.get_object(build_file.fileRef)
                    if 'path' in file_ref and ProjectFiles._path_leaf(path) == ProjectFiles._path_leaf(
                            file_ref.path) \
                            and target in potential_targets:
                        potential_targets.remove(target)
            targets = [target.name for target in potential_targets]
            if targets.__contains__(target_name) == True:
                return False
        return True


    def _filter_targets_without_path(self, project:XcodeProject, path, target_name):
        potential_targets = project.objects.get_targets(target_name)
        for target in potential_targets.copy():
            for build_phase_id in target.buildPhases:
                build_phase = project.get_object(build_phase_id)
                for build_file_id in build_phase.files:
                    build_file = project.get_object(build_file_id)
                    if build_file is None:
                        continue
                    if 'fileRef' not in build_file:
                        continue
                    # print("build_file:",build_file)
                    file_ref = project.get_object(build_file.fileRef)
                    if 'path' in file_ref and ProjectFiles._path_leaf(path) == ProjectFiles._path_leaf(file_ref.path) \
                            and target in potential_targets:
                        potential_targets.remove(target)

        return [target.name for target in potential_targets]

